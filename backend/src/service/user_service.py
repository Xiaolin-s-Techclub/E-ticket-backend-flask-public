from flask import redirect, url_for, flash, make_response, jsonify
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from backend.src.model.User import User, UserSchema
from backend.src.config.config import logger, STUDENT_VALIDATION_INFO, convert_username_to_hash

from backend.src.mail_sender_SES import send_raw_email
from backend.src.QRcode_generator import gen_qrcode


def login(username, email, input_password):
    logger.warning('login()')
    try:
        user = User.get_user(username=username, email=email)
        if user:
            if check_password_hash(user.password_hash, input_password):
                login_user(user)
                return redirect(url_for('xiao_admin'))
            else:
                flash("Password is incorrect")
                logger.warning(f"[!]Password is incorrect")
                # return redirect(url_for('/admin/login'))
                return 'password is incorrect'
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        # return redirect(url_for('fail.html', message="User not found for admin login"))
        flash("User not found")
        logger.warning(f"[!]User not found")
        return 'user not found'


@login_required
def logout():
    try:
        logout_user()
        output = {"result": True, "msg": "Success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": "User not found", "code": 404}
    return output


def create_user(userid, username, first_name, last_name, privilege, password, email, grade, classes,
                student_number):
    try:
        user = User.create_user(userid=userid, username=username, first_name=first_name, last_name=last_name,
                                    # student_uuid=student_uuid,
                                    privilege=privilege, password=password, email=email, grade=grade,
                                    classes=classes, student_number=student_number)
        user_schema = UserSchema()
        output = {"result": True, "msg": user_schema.dump(user), "code": 201}
        # if "@mita-is.ed.jp" in email:
        # else:
        #     output = {"result": None, "msg": "Invalid email address - Please use school email address",
                    #   "code": 400}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        if "Duplicate entry" in str(e):
            output = {"result": None, "msg": "ticket already created for user.",
                      "code": 400}
        else:
            output = {"result": None, "msg": "User not created", "code": 400}
    return jsonify(output)


def validate_ticket_request(userid, ticket_quantity):
    return User.validate_ticket_request(userid, ticket_quantity)


def complete_ticket_request(userid, ticket_quantity):
    return User.commit_ticket_request(userid, ticket_quantity)


def validate_user_info(school_grades, classes, student_number, email=None):
    try:
        if int(student_number) <= STUDENT_VALIDATION_INFO[school_grades][classes]:
            return True
        else:
            logger.error("user_info_validation_error - invalid student number:", school_grades, classes, student_number)
            return False
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        logger.error("user_info_validation_error - cannot validate student info", school_grades, classes,
                     student_number)
        return False


### API Functions

def get_user_by_userid(userid):
    try:
        user = User.get_user_by_userid(userid)
        if user:
            user_schema = UserSchema()
            output = {"result": True, "msg": user_schema.dump(user), "code": 200}
        else:
            output = {"result": False, "msg": "User not found", "code": 404}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": "User not found - internal server error", "code": 404}
    return make_response(jsonify(output))


def get_all_users(limit):
    try:
        users = User.get_all_users(limit=limit)
        user_schema = UserSchema(many=True)
        output = {"result": True, "msg": user_schema.dump(users), "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))


def delete_user_by_userid(userid):
    try:
        user = User.delete_user_by_userid(userid)
        user_schema = UserSchema()
        output = {"result": True, "msg": user_schema.dump(user), "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))


def count_all_users():
    try:
        count_users = User.count_all_users()
        output = {"result": count_users, "msg": "Success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "Cannot count users, please check server", "code": 404}
    return make_response(jsonify(output))


def reset_ticket_application():
    try:
        user_count = User.reset_ticket_application()
        output = {"result": True, "msg": f"reset: {user_count} users. BUT EXISTING tickets were NOT deleted",
                  "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": False, "msg": "Cannot reset ticket application, please check server", "code": 404}
    return make_response(jsonify(output))


def resend_ticket_to_user(userid, ticket_amount):
    try:
        user = User.get_user_by_userid(userid)
        user_dict = {}
        for i in range(1, int(ticket_amount) + 1):
            i = str(i).zfill(2)
            user_dict[userid + f"_{i}"] = f"{i}枚目"

        send_raw_email(to=user.email, userid_dict=user_dict)

        output = {"result": user_dict, "msg": "success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))


def print_save_ticket(userid, ticket_id, invited_name):
    try:
        user_ticket_id = userid + str(ticket_id).zfill(2)
        user_ticket_id_filename = userid + "_" + str(ticket_id).zfill(2)
        gen_qrcode(ticket_hash=convert_username_to_hash(user_ticket_id), guest_name=invited_name,
                   filename=user_ticket_id_filename)

        output = {"result": user_ticket_id_filename, "msg": "Success", "code": 200}
    except Exception as e:
        logger.error(f"[!]Error: {e}")
        output = {"result": None, "msg": "User not found", "code": 404}
    return make_response(jsonify(output))
