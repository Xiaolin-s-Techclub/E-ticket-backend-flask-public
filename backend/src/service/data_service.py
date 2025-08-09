import requests
from flask import make_response, jsonify
import csv
from datetime import datetime

from backend.src.config.config import CONFIG, logger, DB_OUTPUT_DIR, JST_TIMEZONE
from backend.src.db import db, establish_sqlite_connection
from backend.src.model.User import User
from backend.src.model.UserTicket import UserTicket


def export_database():
    user_data = db.session.query(User).all()
    user_ticket_data = db.session.query(UserTicket).all()
    conn = establish_sqlite_connection()
    print(conn)
    for user in user_data:
        conn.merge(user)
    for user_ticket in user_ticket_data:
        conn.merge(user_ticket)

    conn.commit()
    conn.close()

    _export_csv(users=user_data, user_tickets=user_ticket_data)

    return make_response(jsonify({"result": True, "msg": "Successfully exported database", "code": 200}))


def _export_csv(users, user_tickets):
    csv_file_path = DB_OUTPUT_DIR + datetime.now(JST_TIMEZONE).strftime("%Y%m%d%H%M") + "_access_control.csv"
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write the header
        header = [column.name for column in User.__table__.columns]
        csv_writer.writerow(header)

        # Write the data
        for user in users:
            row = [getattr(user, column) for column in header]
            csv_writer.writerow(row)

        # Write the header
        header2 = [column.name for column in UserTicket.__table__.columns]
        csv_writer.writerow(header2)

        # Write the data
        for user_ticket in user_tickets:
            row = [getattr(user_ticket, column) for column in header2]
            csv_writer.writerow(row)

    print(f"Data exported to {csv_file_path}")


def create_test_tickets():
    try:
        try:
            data = {
                "last_name": "DOE",
                "first_name": "JOHN",
                "email": "student@example.com",
                "email_confirm": "student@example.com",
                "school_grades": "S2",
                "classes": "E",
                "student_number": "12",
                "student_school_uuid": "1234567",
                "ticket_quantity": "5",
                "guestName1": "JOHN DOE1",
                "guestName2": "JOHN DOE2",
                "guestName3": "JOHN DOE3",
                "guestName4": "JOHN DOE4",
                "guestName5": "JOHN DOE5"
            }
            response = requests.post(CONFIG.SERVER_URL + 'confirm',
                                     data=data,
                                     timeout=4)
            print(response.text)
            if response.status_code == 200:
                output = {"result": True, "msg": "Successfully created test tickets", "code": 200}
            else:
                output = {"result": False, "msg": "Failed to create test tickets", "code": 500}
        except requests.exceptions.ConnectionError:
            return {"result": False, "msg": "Cannot connect to server"}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": f"Error when creating test tickets: {e}", "code": 500}
    print(output)
    # return make_response(jsonify(output))

# def output_data(day):
#     user_data = db.session.query(User).all()
#     user_ticket_data = db.session.query(UserTicket).all()
#     conn = establish_sqlite_connection()
#     print(conn)
#     for user in user_data:
#         conn.merge(user)
#     for user_ticket in user_ticket_data:
#         conn.merge(user_ticket)
#
#     conn.commit()
#     conn.close()
#
#     _export_csv(users=user_data, user_tickets=user_ticket_data)
#
#     return make_response(jsonify({"result": True, "msg": "Successfully exported database", "code": 200}))

if __name__ == '__main__':
    # export_database()
    # create_test_tickets()
    print(datetime.now().strftime("%Y%m%d%H%M") + "_access_control")
