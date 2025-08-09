from flask_login import UserMixin, login_user, logout_user, login_required
from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash
from datetime import datetime
import pytz

from backend.src.db import db, Base, ma, login_manager, establish_sqlite_connection
from backend.src.config.config import logger, USER_TABLE_NAME, MAX_USER_TICKET_REQUEST_NUM


class User(UserMixin, db.Model):
    __tablename__ = USER_TABLE_NAME
    userid = Column(String(50), primary_key=True, unique=True, nullable=False)
    username = Column(String(50), nullable=False)
    # student_uuid = Column(Integer, nullable=False)  # student uuid like 1234567

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

    privilege = Column(String(25), nullable=False)  # student, teacher, admin-xtc, admin-mif, etc.
    grade = Column(String(5))  # Assuming grades are with letters like S2, S3, etc.
    class_number = Column(String(5))  # Assuming class number is up to 2 digits
    student_number = Column(Integer)  # Assuming student number is up to 4 digits
    email = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255))
    # login_datetime = Column(DateTime)

    music_fes24_requested_ticket_number = Column(Integer, default=0, nullable=False)

    def __init__(self, userid, username, first_name, last_name, privilege, password_hash, email, grade,
                 classes, student_number):
        self.userid = userid
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        # self.student_uuid = student_uuid
        self.privilege = privilege
        self.grade = grade
        self.class_number = classes
        self.student_number = student_number
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def session_commit():
        db.session.commit()

    def get_id(self):
        return self.username

    @staticmethod
    def get_user(username, email):
        return db.session.query(User).filter_by(username=username, email=email).first()

    @staticmethod
    def get_all_users(limit=10):
        return db.session.query(User).limit(limit).all()

    @staticmethod
    def count_all_users():
        return db.session.query(User).count()

    @staticmethod
    def create_user(userid, username, first_name, last_name, email, privilege, password, grade, classes,
                    student_number):
        if password:
            hashed_password = generate_password_hash(password)
        else:
            hashed_password = None
        user = User(userid=userid, username=username, first_name=first_name, last_name=last_name,
                    # student_uuid=student_uuid,
                    email=email, privilege=privilege, password_hash=hashed_password,
                    grade=grade, classes=classes, student_number=student_number)
        db.session.add(user)
        User.session_commit()
        logger.error(f"Created user: {userid}")
        return user

    @staticmethod
    def get_user_by_userid(userid):
        return db.session.query(User).filter_by(userid=userid).first()

    @staticmethod
    def delete_user_by_userid(userid):
        user = db.session.query(User).filter_by(userid=userid).first()
        db.session.delete(user)
        return user

    @staticmethod
    def validate_ticket_request(userid, ticket_quantity: int):
        logger.error(f'userid: {userid}')
        user = db.session.query(User) \
            .filter(User.userid == userid) \
            .with_for_update() \
            .first()
        if user is None:
            if (ticket_quantity) <= MAX_USER_TICKET_REQUEST_NUM:
                return {'validation': True, 'requested_ticket_num': 0, 'is_exist': False}
            else:
                return {'validation': False, 'requested_ticket_num': 0, 'is_exist': False}
        elif (user.music_fes24_requested_ticket_number + ticket_quantity) <= MAX_USER_TICKET_REQUEST_NUM:
            # print(ticket_quantity)
            return {'validation': True, 'requested_ticket_num': user.music_fes24_requested_ticket_number, 'is_exist': True}
        elif (user.music_fes24_requested_ticket_number + ticket_quantity) > MAX_USER_TICKET_REQUEST_NUM:
            return {'validation': False, 'requested_ticket_num': MAX_USER_TICKET_REQUEST_NUM, 'is_exist': True}
        else:
            raise ValueError("cannot verify requested ticket (id or quantity)")

    @staticmethod
    def reset_ticket_application():
        users = db.session.query(User).all()
        for user in users:
            user.music_fes24_requested_ticket_number = 0
        User.session_commit()
        return len(users)

    @staticmethod
    def commit_ticket_request(userid, ticket_quantity):
        user = db.session.query(User).filter(User.userid == userid).with_for_update().first()
        user.music_fes24_requested_ticket_number += ticket_quantity
        User.session_commit()
        return user

    @staticmethod
    def export_database():
        user_ticket_data = db.session.query(User).all()
        # user_data = db.session.query(USER_SQLITE).all()
        # db.session.bind = ['backup']
        # db.session.merge(data)
        # conn: sqlalchemy.orm.Session = _establish_sqlite_connection()
        conn = establish_sqlite_connection()
        print(conn)
        for user in user_ticket_data:
            # print(user.username)
            conn.merge(user)
            # dst_conn.add(local_data)
        conn.commit()
        conn.close()
        # db.session.commit()
        # db.session.close()
        return True


@login_manager.user_loader
def load_user(userid):
    return db.session.query(User).get(userid)


# def login(username, email, password):
# 	user = db.session.query(User).filter_by(username=username, email=email, password=password).first()
# 	return user


# def logout(username):
# 	user = db.session.query(User).get(username)
# 	user.
# 	db.session.commit()
# 	return True

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


if __name__ == "__main__":
    from backend.src.app import app

    with app.app_context():
        # Create the database tables.
        db.create_all()
    # 	# Create a test user
    # 	user = _create_admin_user("admin", "admin@example.com", "default_password")
    # User.verify_request_ticket("S2E12", 1)
    pass
