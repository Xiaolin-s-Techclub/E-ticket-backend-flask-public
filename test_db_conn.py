import time
import psycopg2
from statistics import mean, median
import datetime
import os

def test_db_performance(connection_string, iterations=100):
    """
    Test database performance including connection time, query latency,
    and basic read/write operations.
    """
    results = {
        'connection_times': [],
        'simple_query_times': [],
        'write_times': [],
        'read_times': [],
        'complex_query_times': []
    }
    
    print("Starting database performance test...")
    
    # Test multiple operations
    for i in range(iterations):
        if i % 10 == 0:
            print(f"Running iteration {i + 1}/{iterations}")
            
        # Test 1: Connection Time
        start_time = time.time()
        conn = psycopg2.connect(connection_string)
        results['connection_times'].append(time.time() - start_time)
        
        cursor = conn.cursor()
        
        # Test 2: Simple Query (SELECT 1)
        start_time = time.time()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        results['simple_query_times'].append(time.time() - start_time)
        
        # Test 3: Write Operation
        start_time = time.time()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS perf_test (id serial PRIMARY KEY, data TEXT, created_at TIMESTAMP)'
        )
        cursor.execute(
            'INSERT INTO perf_test (data, created_at) VALUES (%s, %s)',
            (f'test_data_{i}', datetime.datetime.now())
        )
        conn.commit()
        results['write_times'].append(time.time() - start_time)
        
        # Test 4: Read Operation
        start_time = time.time()
        cursor.execute('SELECT * FROM perf_test ORDER BY id DESC LIMIT 1')
        cursor.fetchone()
        results['read_times'].append(time.time() - start_time)
        
        # Test 5: Complex Query
        start_time = time.time()
        cursor.execute('''
            SELECT 
                DATE_TRUNC('second', created_at) as time_bucket,
                COUNT(*) as count,
                MAX(created_at) as latest_entry
            FROM perf_test 
            GROUP BY DATE_TRUNC('second', created_at)
            ORDER BY time_bucket DESC
            LIMIT 5
        ''')
        cursor.fetchall()
        results['complex_query_times'].append(time.time() - start_time)
        
        cursor.close()
        conn.close()
    
    # Clean up test table
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS perf_test')
    conn.commit()
    cursor.close()
    conn.close()
    
    # Analyze results
    print("\nPerformance Test Results:")
    print("------------------------")
    
    for operation, times in results.items():
        avg_time = mean(times) * 1000  # Convert to milliseconds
        med_time = median(times) * 1000
        max_time = max(times) * 1000
        min_time = min(times) * 1000
        
        print(f"\n{operation.replace('_', ' ').title()}:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Median:  {med_time:.2f}ms")
        print(f"  Max:     {max_time:.2f}ms")
        print(f"  Min:     {min_time:.2f}ms")

    return results

connection_string = os.environ.get('DATABASE_URL', "postgresql://username:password@localhost:5432/database_name")

# Run the test
results = test_db_performance(connection_string, iterations=100)
