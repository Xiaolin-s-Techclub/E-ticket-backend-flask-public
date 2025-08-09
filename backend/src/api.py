from flask import Blueprint, request, jsonify
import backend.src.logger as logger_wrapper
from backend.src.config.config import logger

import backend.src.auth as auth
from backend.src.service import user_ticket_service, user_service, data_service

# https://www.youtube.com/watch?v=GMppyAPbLYk

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# todo configure logging setting properly

### USER TICKET APIs

@api_bp.route('/entry/validate/<ticket_hash>', methods=['GET'])
@logger_wrapper.http_request_logging
def validate_entry(ticket_hash):
    return user_ticket_service.validate_entry(ticket_hash=ticket_hash)


@api_bp.route('/entry/total_number', methods=['GET'])
@logger_wrapper.http_request_logging
def current_total_entry_status():
    return user_ticket_service.current_total_entry_status()


@api_bp.route('/exit/validate/<user_hash>', methods=['GET'])
@logger_wrapper.http_request_logging
def validate_exit(user_hash):
    return user_ticket_service.validate_exit(ticket_hash=user_hash)


@api_bp.route('/exit/total_number', methods=['GET'])
@logger_wrapper.http_request_logging
def current_total_exit_status():
    return user_ticket_service.current_total_exit_status()


@api_bp.route('/ticket/id/<userid>/<ticket_id>', methods=['GET', 'DELETE'])
@logger_wrapper.http_request_logging
@auth.requires_auth
def get_user_ticket_by_userid(userid, ticket_id):
    if request.method == 'GET':
        return user_ticket_service.get_user_ticket_by_user_ticket_id(userid=userid, ticket_id=ticket_id)
    if request.method == 'DELETE':
        return user_ticket_service.delete_user_ticket_by_userid(userid=userid, ticket_id=ticket_id)


@api_bp.route('/ticket/hash/<ticket_hash>', methods=['GET'])
@logger_wrapper.http_request_logging
@auth.requires_auth
def get_user_by_user_hash(ticket_hash):
    return user_ticket_service.get_user_ticket_by_ticket_hash(ticket_hash=ticket_hash)


@api_bp.route('/ticket/limit/<limit>', methods=['GET'])
@logger_wrapper.http_request_logging
def get_all_user_tickets(limit):
    return user_ticket_service.get_all_user_tickets(limit=limit)


@api_bp.route('/ticket/all/total_number', methods=['GET'])
@logger_wrapper.http_request_logging
@auth.requires_auth
def get_total_user_number():
    return user_ticket_service.get_total_user_ticket_number()


@api_bp.route('/ticket/<userid>/<ticket_id>/<invited_name>', methods=['POST'])
@logger_wrapper.http_request_logging
@auth.requires_auth
def create_user(userid, ticket_id, invited_name):
    user_hash, result = user_ticket_service.create_user_ticket_by_user_ticket_id(userid=userid,
                                                                                 ticket_id=ticket_id,
                                                                                 invited_name=invited_name)
    return result

# # DANGEROUS, integrated with same path as "ticket/id/<userid>/<ticket_id>"
# @api_bp.route('/user/<userid>/<ticket_id>', methods=['DELETE'])
# @logger_wrapper.http_request_logging
# @auth.requires_auth
# def delete_user_from_db(userid, ticket_id):
#     return user_ticket_service.delete_user_ticket_by_userid(userid=userid, ticket_id=ticket_id)


@api_bp.route('/ticket/all/<force>', methods=['DELETE'])
@logger_wrapper.http_request_logging
@auth.requires_auth
def delete_all_users(force):
    return None
    return user_ticket_service.delete_all_user_tickets(force=force)


@api_bp.route('ticket/all/reset_ticket_usage/<force>', methods=['GET'])
@logger_wrapper.http_request_logging
@auth.requires_auth
def reset_all_user_ticket_usage(force):
    return user_ticket_service.reset_ticket_usage(force=force)


### USER APIs

@api_bp.route('/user/id/<userid>', methods=['GET', 'DELETE'])
@logger_wrapper.http_request_logging
def get_user_by_userid(userid):
    if request.method == 'GET':
        return user_service.get_user_by_userid(userid=userid)
    if request.method == 'DELETE':
        return user_service.delete_user_by_userid(userid=userid)


@api_bp.route('/user/limit/<limit>', methods=['GET'])
@logger_wrapper.http_request_logging
def get_all_users(limit):
    return user_service.get_all_users(limit=limit)


@api_bp.route('/user/all/total_number', methods=['GET'])
@logger_wrapper.http_request_logging
def get_total_user_ticket_number():
    return user_service.count_all_users()


# redirect to ticket/all/reset_ticket_usage/<force>
@api_bp.route('/user/all/reset_ticket_usage/<force>', methods=['GET'])
def reset_all_ticket_usage(force):
    return reset_all_user_ticket_usage(force=force)


@api_bp.route('/user/all/reset_ticket_application', methods=['GET'])
def reset_ticket_application():
    return user_service.reset_ticket_application()
    #todo add to api-doc


@api_bp.route('/user/resend_ticket/<userid>/<ticket_amount>', methods=['GET'])
@logger_wrapper.http_request_logging
def resend_ticket_to_user(userid, ticket_amount):
    return user_service.resend_ticket_to_user(userid=userid, ticket_amount=ticket_amount)


@api_bp.route('/user/print_ticket/<userid>/<ticket_id>/<invited_name>', methods=['POST'])
@logger_wrapper.http_request_logging
def print_save_ticket(userid, ticket_id, invited_name):
    return user_service.print_save_ticket(userid=userid, ticket_id=ticket_id, invited_name=invited_name)

### DATA APIs

@api_bp.route('/data/export_database', methods=['GET'])
@logger_wrapper.http_request_logging
@auth.requires_auth
def export_backup():
    return data_service.export_database()


@api_bp.route('/data/create_test_tickets', methods=['GET'])
@logger_wrapper.http_request_logging
def create_test_tickets():
    return data_service.create_test_tickets()


# todo create admin role commands - clear qrcode gen folder, clear db, etc


if __name__ == '__main__':
    pass
