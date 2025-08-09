from flask import make_response, jsonify
from backend.src.config.config import logger, DAY, convert_username_to_hash, JST_TIMEZONE
from backend.src.model.UserTicket import UserTicket, UserTicketSchema

from backend.src.service import user_service
from backend.src.service.data_service import export_database

from datetime import datetime
import pytz


# DBから抽出したRawデータを加工する目的。
# ビジネスロジックを管理する。

def get_all_user_tickets(limit):
    try:
        users = UserTicket.get_all_user_tickets(limit=limit)
        user_ticket_schema = UserTicketSchema(many=True)
        output = {"result": user_ticket_schema.dump(users), "msg": "Success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))


def get_user_ticket_by_user_ticket_id(userid, ticket_id):
    try:
        user = UserTicket.get_user_ticket_by_user_ticket_id(userid, ticket_id)
        user_ticket_schema = UserTicketSchema()
        output = {"result": user_ticket_schema.dump(user), "msg": "Success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))


def get_user_ticket_by_ticket_hash(ticket_hash):
    try:
        user = UserTicket.get_user_ticket_by_ticket_hash(ticket_hash)
        user_ticket_schema = UserTicketSchema()
        output = {"result": user_ticket_schema.dump(user), "msg": "Success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))


def create_user_ticket_by_user_ticket_id(userid: str, invited_name: str, ticket_id: int = None):
    if ticket_id is None:
        ticket_id = user_service.validate_ticket_request(userid, ticket_quantity=1)['requested_ticket_num'] + 1
    ticket_hash = convert_username_to_hash(userid + str(ticket_id).zfill(2))
    try:
        result, user = UserTicket.create_user_ticket(userid, ticket_id, invited_name, ticket_hash)
        user_ticket_schema = UserTicketSchema()
        output = {"result": user_ticket_schema.dump(user), "msg": "Success", "code": 201}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        if "Duplicate entry" in str(e):
            msg = "duplicate entry - ticket already created with that info. Surpassed available ticket requests?"
        else:
            msg = "User not created"
        output = {"result": "Failed", "msg": msg, "code": 400}
    return output, make_response(jsonify(output))


def delete_user_ticket_by_userid(userid, ticket_id):
    try:
        user = UserTicket.delete_user_ticket(userid=userid, ticket_id=ticket_id)
        user_ticket_schema = UserTicketSchema()
        output = {"result": True, "msg": user_ticket_schema.dump(user), "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))


def _get_current_timestamp():
    return datetime.now(JST_TIMEZONE)


def validate_entry(ticket_hash):
    try:
        user_ticket = UserTicket.get_user_ticket_by_ticket_hash(ticket_hash)
        msg = "Welcome, " + user_ticket.invited_name + "!"
        if DAY == 1:
            if user_ticket.entry_day1 >= 1:
                user_ticket.entry_day1 -= 1
                user_ticket.entry_total_day1 += 1
                user_ticket.entry_time_day1 = _get_current_timestamp()
                result = True
                code = 200
            else:
                result = False
                code = 400
                msg = f"{user_ticket.userid}: 使用済みチケット(DAY1)"
                logger.error(user_ticket.entry_time_day1)
        elif DAY == 2:
            if user_ticket.entry_day2 >= 1:
                user_ticket.entry_day2 -= 1
                user_ticket.entry_total_day2 += 1
                user_ticket.entry_time_day2 = _get_current_timestamp()
                result = True
                code = 200
            else:
                result = False
                code = 400
                msg = f"{user_ticket.userid}: 使用済みチケット(DAY2)"
                logger.error(user_ticket.entry_time_day2)
        else:
            result = False
            code = 400
            msg = "Invalid Day Setting - Please contact the operator"
            logger.error("[!]Invalid Day Setting - variable DAY is neither 1 or 2 but was: " + str(DAY))
        UserTicket.session_commit()
        output = {"code": code, "result": result, "msg": msg}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))


def validate_exit(ticket_hash):
    try:
        user_ticket = UserTicket.get_user_ticket_by_ticket_hash(ticket_hash)
        msg = "Thank you for visiting!"
        logger.error(user_ticket.entry_day1)
        if DAY == 1:
            if user_ticket.entry_day1 == 0:
                user_ticket.entry_day1 = 1
                user_ticket.exit_day1 += 1
                logger.error("updated usage!")
                user_ticket.exit_time_day1 = _get_current_timestamp()
                # db.session.commit()
                result = True
                code = 200
            elif user_ticket.entry_day1 == 1 or user_ticket.entry_day1 == 2:
                logger.error(
                    f"[!]User {user_ticket.userid}, {ticket_hash}\n has not entered yet but tried to exit, " + str(DAY))
                result = False
                code = 400
                msg = f"{user_ticket.userid} has not entered yet but tried to exit - Please contact the operator"
            else:
                result = False
                code = 400
        elif DAY == 2:
            if user_ticket.entry_day2 == 0 or user_ticket.userid == "S2A07":
                user_ticket.entry_day2 += 1
                user_ticket.exit_day2 += 1
                user_ticket.exit_time_day2 = _get_current_timestamp()
                # db.session.commit()
                result = True
                code = 200
            else:
                logger.error(
                    f"[!]User {user_ticket.userid}, {ticket_hash}\n has not entered yet but tried to exit, " + str(DAY))
                result = False
                code = 400
                msg = f"{user_ticket.userid} User has not entered yet but tried to exit - Please contact the operator"
        else:
            msg = "DAY is neither 1 nor 2"
            result = False
            code = 400
        UserTicket.session_commit()
        output = {'code': code, "result": result, "msg": msg}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))


def current_total_entry_status():
    try:
        result = UserTicket.current_total_entry_status()
        output = {"result": result, "msg": "Success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "Server internal error", "code": 500}
    return make_response(jsonify(output))


def current_total_exit_status():
    try:
        result = UserTicket.current_total_exit_status()
        output = {"result": result, "msg": "Success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "Server internal error", "code": 500}
    return make_response(jsonify(output))


def get_total_user_ticket_number():
    try:
        result = UserTicket.get_total_number_user_ticket()
        output = {"result": result, "msg": "Success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "Server internal error", "code": 500}
    return make_response(jsonify(output))


def delete_all_user_tickets(force):
    try:
        result = UserTicket.delete_all_user_tickets_from_db(force=force)
        user_service.reset_ticket_application()
        if result is True:
            msg = "All user tickets deleted"
        else:
            msg = "Operation was not forced. No data was deleted"
        output = {"result": result, "msg": msg, "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": "Server internal error", "code": 500}
    return make_response(jsonify(output))


def reset_ticket_usage(force):
    if force == "force":
        _force = True
    else:
        _force = False
    try:
        UserTicket.reset_user_ticket_usage(force=_force)
        output = {"result": True, "msg": "Success. BUT users ticket application were NOT reset", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": "Server internal error", "code": 500}
    return make_response(jsonify(output))


# deprecated
# def export_backup():
#     try:
#         result = export_database()
#         output = {"result": result, "msg": "Success", "code": 200}
#     except Exception as e:
#         logger.error(f"[!]Error: {e}")
#         output = {"result": False, "msg": f"Error when exporting db: {e}", "code": 500}
#     return make_response(jsonify(output))


