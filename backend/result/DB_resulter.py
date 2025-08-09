import DB_editor
from DB_editor import User
import glob


def count_db_ticket_usage(conn):
    count = 0
    # users = conn.query(User).filter(User.entry > 0).filter(User.entry_time < datetime(2024, 2, 8,12, 0, 0)).all()　　["1", '2', '3']
    users = conn.query(User).filter(User.entry > 0).all()
    for user in users:
        if list(user.userid)[0] in ['4', '5', '6']:
            print(f"{user.username}: {user.userid}")
            count += 1
    print(f"Total Guests: {count}")

def check_ticket_usage_time(conn, userid):
    user = conn.query(User).filter(User.userid == userid).first()
    return user.entry_time

def count_log_ticket_usage(directory='morning'):
    result_log_dir = glob.glob(f'result_log/{directory}/*')
    # result_log_a_dir = glob.glob('result_log/afternoon/*')

    successful_count = 0
    successful_userid = []
    error_count = 0
    error_0_userid = []
    error_1_userid = []

    for log in result_log_dir:
        with open(log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.split(":")
                if line[1] == " successful!\n":
                    successful_count += 1
                    successful_userid.append(line[0])
                elif line[1].split(" - ")[0] == "[0]":
                    error_count += 1
                    error_0_userid.append(line[0])
                elif line[1].split(" - ")[0] == "[1]":
                    error_count += 1
                    error_1_userid.append(line[0])
                    print(f"{line[0]} used: {check_ticket_usage_time(conn, line[0])}, and again at {line[1].split(' - ')[1]}")

    print(f"Morning: successful: {successful_count}, error: {error_count}")
    print("[0]" + str(error_0_userid))
    print("[1]" + str(error_1_userid))


if __name__ == '__main__':
    handler = DB_editor.sql_ConnectionHandler(echo_option=False)
    conn, _connection_method = handler.establish_connection(connection_method="sqlite")


    # count_db_ticket_usage(conn)


    count_log_ticket_usage('morning')
    count_log_ticket_usage('afternoon')
