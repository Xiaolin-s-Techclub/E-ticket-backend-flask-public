import sqlalchemy.orm

from backend.src.config.config import DB_OUTPUT_DIR, TABLE_NAME, USER_TABLE_NAME, JST_TIMEZONE

from datetime import datetime
import pytz

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy  # 追加
from flask_marshmallow import Marshmallow  # 追加

from sqlalchemy import create_engine, Column, Integer, String, DATETIME, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

Base = declarative_base()


# db = SQLAlchemy(model_class=User)  # 追加
db = SQLAlchemy()  # 追加
ma = Marshmallow()
login_manager = LoginManager()


def init_db(app):
    db.init_app(app)
    # db.create_all()


def init_ma(app):
    ma.init_app(app)


def init_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = "users.login"


def establish_sqlite_connection(echo_option=True):
    DB_name = DB_OUTPUT_DIR + datetime.now(JST_TIMEZONE).strftime("%Y%m%d%H%M") + "_access_control"
    # DB_name = "access_controll"
    print(DB_name)
    try:
        engine = create_engine(f"sqlite:///{DB_name}.db",
                               echo=echo_option)
    except Exception as e:
        print(e)
    finally:
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        conn = Session()
    return conn


# def add_user_ticket_to_db(userid, user_hash, invited_name):
#     # for num_ticket in range(1, ticket_per_user + 1):
#     db.session.add(User(userid=userid, invited_name=invited_name, user_hash=user_hash))
#     logger.info(f"Added user ticket: {userid}")
#     db.session.commit()  # flash it
#
#
# def _validate_entry(user_hash):
#     user = db.session.query(User).filter_by(user_hash=user_hash).first()
#     if DAY == 1:
#         if user.entry_day1 == 1:
#             user.entry_day1 = 0
#             user.entry_total += 1
#             db.session.commit()
#             result = True
#         else:
#             result = False
#     elif DAY == 2:
#         if user.entry_day2 == 1:
#             user.entry_day2 = 0
#             user.entry_total += 1
#             db.session.commit()
#             result = True
#         else:
#             result = False
#     else:
#         result = False
#     return {"result": result}
#
#
# def _validate_exit(user_hash):
#     user = db.session.query(User).filter_by(user_hash=user_hash).first()
#     if DAY == 1:
#         if user.entry_day1 == 0:
#             user.entry_day1 = 1
#             db.session.commit()
#             result = True
#         elif user.entry_day1 == 1:
#             logger.error(f"User {user.username}, {user_hash}\n has not entered yet but tried to exit")
#             result = False
#         else:
#             result = False
#     elif DAY == 2:
#         if user.entry_day2 == 0:
#             user.entry_day2 = 1
#             db.session.commit()
#             result = True
#         else:
#             result = False
#     else:
#         result = False
#     return {"result": result}
#
#
# def _current_total_entry_status():
#     result = db.session.query(User).filter_by(entry_day1=0).count() if DAY == 1 else db.session.query(User).filter_by(
#         entry_day2=0).count()
#     return {"current_total_entry": result}
#
#
# #
# def _delete_all_users_from_db(force=False):
#     # if input(f"Are you sure you want to delete all data from database?(y/n) ") == "y":
#     if force:
#         db.session.query(User).delete()
#         db.session.commit()
#
#
# #
# def _reset_ticket_usage(force=False):
#     # if input("Are you sure you want to reset ticket usage of all users?(y/n) ") == "y":
#     if force:
#         user = db.session.query(User).all()
#         if DAY == 1:
#             user.entry_day1 = 1
#             user.entry_time = None
#             user.exit_time = None
#         elif DAY == 2:
#             user.entry_day2 = 1
#             user.entry_time = None
#             user.exit_time = None
#         db.session.commit()
#
#
# def _modify_user_entry_time(username, count, force=False):
#     # if input(f"Are you sure you want to reset ticket usage of {username}?(y/n) ") == "y":
#     if force:
#         user = db.session.query(User).filter_by(username=username).first()
#         if DAY == 1:
#             user.entry_day1 = count
#         elif DAY == 2:
#             user.entry_day2 = count
#         db.session.commit()

#
# def export_database():
#     user_ticket_data = db.session.query(UserTicket).all()
#     user_data = db.session.query(User).all()
#     # db.session.bind = ['backup']
#     # db.session.merge(data)
#     conn: sqlalchemy.orm.Session = establish_sqlite_connection()
#     print(conn)
#     for user in user_ticket_data:
#         # print(user.username)
#         conn.merge(user)
#         # dst_conn.add(local_data)
#     for user_data in user_data:
#         conn.merge(user_data)
#     conn.commit()
#     conn.close()
#     # db.session.commit()
#     # db.session.close()
#     return True


#
# # conn.add(User(username="username", userid="userid", entry="entry"))
# # results = conn.query(User).all()
# # results = conn.query(User).filter(User.username == "S1E0101").all()
# # pprint(results)


if __name__ == '__main__':
    # _establish_sqlite_connection()
    pass
    # handler = sql_ConnectionHandler(echo_option=True)
    # conn, _connection_method = handler.establish_connection(connection_method="mysql")

    # delete_all_from_db(conn, handler)
    # add_user_to_db(conn, max_no_students=40, ticket_per_user=1)

    # reset_ticket_usage(conn, force=True)

    # export_database(conn)
    #
    # handler.close()

    # db.create_all()
    # with app.app_context():
    #     # db.create_all()
    #     add_user_ticket_to_db(username='S2E1201', user_hash='', invited_name='Sota Kobayashi 1st')


### deprecated

# class UserTICKET_SQLITE(Base):
#     __tablename__ = TABLE_NAME
#
#     userid = Column(String(255), nullable=False)
#     ticket_id = Column(Integer, autoincrement=True, nullable=False)
#     created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
#     invited_name = Column(String(225), nullable=False)
#     ticket_hash = Column(String(225), nullable=False)
#     entry_day1 = Column(Integer, default=1)
#     entry_day2 = Column(Integer, default=1)
#     exit_day1 = Column(Integer, default=0)
#     exit_day2 = Column(Integer, default=0)
#     entry_total = Column(Integer, default=0)
#     entry_time_day1 = Column(DATETIME)
#     entry_time_day2 = Column(DATETIME)
#     exit_time_day1 = Column(DATETIME)
#     exit_time_day2 = Column(DATETIME)
#
#     def __repr__(self):
#         return f"({self.userid})\n   DAY1: {self.entry_day1})\n   DAY2: {self.entry_day2}"
#
#     def __init__(self, userid, ticket_id, invited_name, ticket_hash):
#         self.userid = userid
#         self.ticket_id = ticket_id
#         self.invited_name = invited_name
#         self.ticket_hash = ticket_hash
#
#
# class USER_SQLITE(Base):
#     __tablename__ = USER_TABLE_NAME
#
#     userid = Column(String(50), primary_key=True, unique=True, nullable=False)
#     username = Column(String(50), nullable=False)
#     student_uuid = Column(Integer, nullable=False)  # student uuid like 1234567
#
#     first_name = Column(String(50), nullable=False)
#     last_name = Column(String(50), nullable=False)
#
#     privilege = Column(String(25), nullable=False)  # student, teacher, admin-xtc, admin-mif, etc.
#     grade = Column(String(5))  # Assuming grades are with letters like S2, S3, etc.
#     class_number = Column(String(5))  # Assuming class number is up to 2 digits
#     student_number = Column(Integer)  # Assuming student number is up to 4 digits
#     email = Column(String(50), nullable=False, unique=True)
#     password_hash = Column(String(255))
#
#     mif24_requested_ticket_number = Column(Integer, default=0, nullable=False)
