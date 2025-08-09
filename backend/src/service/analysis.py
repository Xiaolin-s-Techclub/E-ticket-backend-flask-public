from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime
import numpy as np


def analyze_ticket_data(connection_string, start_date=None, end_date=None):
    """
    Analyze ticket usage data from MySQL database.

    Parameters:
    connection_string (str): SQLAlchemy connection string for MySQL
    start_date (str, optional): Start date in 'YYYY-MM-DD' format
    end_date (str, optional): End date in 'YYYY-MM-DD' format

    Returns:
    tuple: (summary_stats, hourly_distribution, usage_patterns)
    """
    engine = create_engine(connection_string)

    # Base query to get ticket data
    query = """
        WITH DailyStats AS (
            SELECT 
                ticket_hash,
                DATE(entry_time_day1) as date1,
                DATE(entry_time_day2) as date2,
                HOUR(entry_time_day1) as hour_day1,
                HOUR(entry_time_day2) as hour_day2,
                remaining_usage_day1,
                remaining_usage_day2,
                HOUR(exit_day1) as exit_hour_day1,
                HOUR(exit_day2) as exit_hour_day2,
                entry_total_day1,
                entry_total_day2
            FROM tickets
            WHERE 1=1
            {% if start_date %}
            AND DATE(entry_time_day1) >= :start_date
            {% endif %}
            {% if end_date %}
            AND DATE(entry_time_day1) <= :end_date
            {% endif %}
        )
        SELECT 
            -- Summary metrics
            COUNT(DISTINCT ticket_hash) as total_tickets,
            AVG(entry_total_day1) as avg_entries_day1,
            AVG(entry_total_day2) as avg_entries_day2,
            AVG(remaining_usage_day1) as avg_remaining_day1,
            AVG(remaining_usage_day2) as avg_remaining_day2,
            SUM(CASE WHEN entry_total_day1 > 0 AND entry_total_day2 > 0 THEN 1 ELSE 0 END) as tickets_used_both_days,
            SUM(CASE WHEN entry_total_day1 = 0 AND entry_total_day2 = 0 THEN 1 ELSE 0 END) as tickets_unused,

            -- Peak hours
            (
                SELECT hour_day1 
                FROM DailyStats 
                GROUP BY hour_day1 
                ORDER BY COUNT(*) DESC 
                LIMIT 1
            ) as peak_hour_day1,

            (
                SELECT hour_day2 
                FROM DailyStats 
                GROUP BY hour_day2 
                ORDER BY COUNT(*) DESC 
                LIMIT 1
            ) as peak_hour_day2,

            -- Full usage counts
            SUM(CASE WHEN remaining_usage_day1 = 0 THEN 1 ELSE 0 END) as full_usage_day1,
            SUM(CASE WHEN remaining_usage_day2 = 0 THEN 1 ELSE 0 END) as full_usage_day2,

            -- Average exit times
            AVG(exit_hour_day1) as avg_exit_time_day1,
            AVG(exit_hour_day2) as avg_exit_time_day2
        FROM DailyStats;
    """

    # Query for hourly distribution
    hourly_query = """
        WITH DailyStats AS (
            SELECT 
                HOUR(entry_time_day1) as hour_day1,
                HOUR(entry_time_day2) as hour_day2
            FROM tickets
            WHERE 1=1
            {% if start_date %}
            AND DATE(entry_time_day1) >= :start_date
            {% endif %}
            {% if end_date %}
            AND DATE(entry_time_day1) <= :end_date
            {% endif %}
        )
        SELECT 
            hour,
            day_number,
            COUNT(*) as entries,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM DailyStats) as percentage
        FROM (
            SELECT hour_day1 as hour, 1 as day_number FROM DailyStats
            UNION ALL
            SELECT hour_day2 as hour, 2 as day_number FROM DailyStats
        ) combined
        WHERE hour IS NOT NULL
        GROUP BY hour, day_number
        ORDER BY day_number, entries DESC;
    """

    # Replace template variables based on whether dates are provided
    for q in [query, hourly_query]:
        q = q.replace(
            "{% if start_date %}", "" if start_date else "-- "
        ).replace(
            "{% endif %}", ""
        ).replace(
            "{% if end_date %}", "" if end_date else "-- "
        )

    # Create parameters dictionary
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    with engine.connect() as conn:
        # Get main statistics
        summary_stats = pd.read_sql(text(query), conn, params=params).to_dict('records')[0]

        # Get hourly distribution
        hourly_dist = pd.read_sql(text(hourly_query), conn, params=params)

    # Process hourly distribution
    hourly_distribution = {
        'day1': hourly_dist[hourly_dist['day_number'] == 1].set_index('hour')[['entries', 'percentage']].to_dict(
            'index'),
        'day2': hourly_dist[hourly_dist['day_number'] == 2].set_index('hour')[['entries', 'percentage']].to_dict(
            'index')
    }

    # Create usage patterns
    usage_patterns = {
        'full_usage_day1': summary_stats['full_usage_day1'],
        'full_usage_day2': summary_stats['full_usage_day2'],
        'avg_exit_time_day1': summary_stats['avg_exit_time_day1'],
        'avg_exit_time_day2': summary_stats['avg_exit_time_day2'],
        'peak_hour_day1': summary_stats['peak_hour_day1'],
        'peak_hour_day2': summary_stats['peak_hour_day2'],
        'hourly_report_day1': [
            {
                'hour': f'{hour:02d}:00',
                'entries': data['entries'],
                'percentage': data['percentage']
            }
            for hour, data in hourly_distribution['day1'].items()
        ],
        'hourly_report_day2': [
            {
                'hour': f'{hour:02d}:00',
                'entries': data['entries'],
                'percentage': data['percentage']
            }
            for hour, data in hourly_distribution['day2'].items()
        ]
    }

    return summary_stats, hourly_distribution, usage_patterns


def print_analysis(connection_string, start_date=None, end_date=None):
    """
    Print a formatted analysis of the ticket data from database.

    Parameters:
    connection_string (str): SQLAlchemy connection string for MySQL
    start_date (str, optional): Start date in 'YYYY-MM-DD' format
    end_date (str, optional): End date in 'YYYY-MM-DD' format
    """
    summary_stats, hourly_distribution, usage_patterns = analyze_ticket_data(
        connection_string, start_date, end_date
    )

    print("=== Ticket Usage Analysis ===\n")

    if start_date and end_date:
        print(f"Period: {start_date} to {end_date}\n")

    print("General Statistics:")
    print(f"Total Tickets: {summary_stats['total_tickets']}")
    print(f"Tickets Used Both Days: {summary_stats['tickets_used_both_days']}")
    print(f"Unused Tickets: {summary_stats['tickets_unused']}\n")

    print("Average Usage:")
    print(f"Day 1 Entries: {summary_stats['avg_entries_day1']:.2f}")
    print(f"Day 2 Entries: {summary_stats['avg_entries_day2']:.2f}\n")

    print("Peak Hours:")
    print(f"Day 1: {usage_patterns['peak_hour_day1']:02d}:00")
    print(f"Day 2: {usage_patterns['peak_hour_day2']:02d}:00\n")

    print("Top 3 Busiest Hours Day 1:")
    for entry in sorted(usage_patterns['hourly_report_day1'],
                        key=lambda x: x['entries'], reverse=True)[:3]:
        print(f"- {entry['hour']}: {int(entry['entries'])} entries ({entry['percentage']:.1f}%)")

    print("\nTop 3 Busiest Hours Day 2:")
    for entry in sorted(usage_patterns['hourly_report_day2'],
                        key=lambda x: x['entries'], reverse=True)[:3]:
        print(f"- {entry['hour']}: {int(entry['entries'])} entries ({entry['percentage']:.1f}%)")


# Example usage:
if __name__ == "__main__":
    connection_string = "mysql+pymysql://user:password@localhost/database"

    # Get all-time statistics
    print_analysis(connection_string)

    # Get statistics for a specific date range
    print("\n=== January 2024 Analysis ===")
    print_analysis(
        connection_string,
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
