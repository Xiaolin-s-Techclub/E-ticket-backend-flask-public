from backend.src.config.config import logger, DAY, TABLE_NAME
from backend.src.db import db, Base, ma
from backend.src.model.User import User
import backend.src.auth as auth
from sqlalchemy.dialects.mysql import TIMESTAMP as Timestamp
from sqlalchemy import text



# class user(Base):
class UserTicket(db.Model):
    __tablename__ = TABLE_NAME
    userid = db.Column(db.String(225), nullable=False)
    ticket_id = db.Column(db.Integer, autoincrement=True, nullable=False)
    created_at = db.Column(Timestamp, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    invited_name = db.Column(db.String(225), nullable=False)
    ticket_hash = db.Column(db.String(225), nullable=False, primary_key=True)
    entry_day1 = db.Column(db.Integer, default=1)
    entry_day2 = db.Column(db.Integer, default=1)
    exit_day1 = db.Column(db.Integer, default=0)
    exit_day2 = db.Column(db.Integer, default=0)
    entry_total_day1 = db.Column(db.Integer, default=0)
    entry_total_day2 = db.Column(db.Integer, default=0)
    entry_time_day1 = db.Column(db.DateTime)
    entry_time_day2 = db.Column(db.DateTime)
    exit_time_day1 = db.Column(db.DateTime)
    exit_time_day2 = db.Column(db.DateTime)

    # Constructor
    def __init__(self, userid, ticket_id, invited_name, ticket_hash):
        self.userid = userid
        self.ticket_id = ticket_id
        self.invited_name = invited_name
        self.ticket_hash = ticket_hash

    def __repr__(self):
        return '<UserTicket %r>' % self.userid


    @staticmethod
    def session_commit():
        db.session.commit()


    @staticmethod
    def get_all_user_tickets(limit=10):
        return db.session.query(UserTicket).limit(limit).all()


    @staticmethod
    def get_user_ticket_by_user_ticket_id(userid, ticket_id):
        result = db.session.query(UserTicket) \
            .filter(UserTicket.userid == userid) \
            .filter(UserTicket.ticket_id == ticket_id) \
            .first()
        return result


    @staticmethod
    def get_user_ticket_by_ticket_hash(ticket_hash):
        result = db.session.query(UserTicket) \
            .filter(UserTicket.ticket_hash == ticket_hash) \
            .with_for_update() \
            .first()
        return result

    @staticmethod
    def create_user_ticket(userid, ticket_id, invited_name, ticket_hash):
        record = UserTicket(
            userid=userid,
            ticket_id=ticket_id,
            ticket_hash=ticket_hash,
            invited_name=invited_name,
        )
        # INSERT INTO users(name) VALUES(...)
        db.session.add(record)
        db.session.commit()
        logger.error(f"Created user ticket: {userid}")

        return True, record

    @staticmethod
    def delete_user_ticket(userid, ticket_id):
        user = db.session.query(UserTicket).filter_by(userid=userid, ticket_id=ticket_id).first()
        db.session.delete(user)
        db.session.commit()
        return user

    @staticmethod
    def current_total_entry_status():
        result = db.session.query(UserTicket).filter_by(entry_day1=0).count() if DAY == 1 else db.session.query(
            UserTicket).filter_by(
            entry_day2=0).count()
        return result


    @staticmethod
    def current_total_exit_status():
        result = db.session.query(UserTicket).filter_by(exit_day1=0).count() if DAY == 1 else db.session.query(
            UserTicket).filter_by(
            exit_day2=0).count()
        return result


    @staticmethod
    def get_total_number_user_ticket():
        return len(db.session.query(UserTicket).all())


    @auth.requires_auth
    @staticmethod
    def delete_all_user_tickets_from_db(force=False):
        # if input(f"Are you sure you want to delete all data from database?(y/n) ") == "y":
        if force == "force":
            db.session.query(UserTicket).delete()
            db.session.commit()
            return True
        else:
            return False

    @auth.requires_auth
    @staticmethod
    def reset_user_ticket_usage(force=True):
        # if input("Are you sure you want to reset ticket usage of all users?(y/n) ") == "y":
        if force:
            user_tickets = db.session.query(UserTicket).all()
            for user in user_tickets:
                if DAY == 1:
                    user.entry_day1 = 1
                    user.entry_total_day1 = 0
                    user.entry_total_day2 = 0
                    user.entry_time_day1 = None
                    user.entry_time_day2 = None
                    user.exit_time_day1 = None
                    user.exit_time_day2 = None
                elif DAY == 2:
                    user.entry_day2 = 1
                    user.entry_total_day1 = 0
                    user.entry_total_day2 = 0
                    user.entry_time_day1 = None
                    user.entry_time_day2 = None
                    user.exit_time_day1 = None
                    user.exit_time_day2 = None

            db.session.commit()

    @staticmethod
    def reset_user_password():
        pass

    @auth.requires_auth
    @staticmethod
    def modify_user_ticket_entry_time(userid, new_count, force=False):
        # if input(f"Are you sure you want to reset ticket usage of {username}?(y/n) ") == "y":
        if force:
            user = db.session.query(UserTicket).filter_by(userid=userid).first()
            if DAY == 1:
                user.entry_day1 = new_count
            elif DAY == 2:
                user.entry_day2 = new_count
            db.session.commit()



# Definition of UserTicket Schema with Marshmallow
# refer: https://flask-marshmallow.readthedocs.io/en/latest/
class UserTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserTicket


if __name__ == "__main__":
    from backend.src.app import app
    with app.app_context():
        # Create the database tables.
        db.drop_all()
        db.create_all()
