import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
from flask_login import LoginManager, login_required
from flask_wtf import CSRFProtect

from backend.src.config.config import FRONT_END_STATIC_DIR, logger, CONFIG
from backend.src.api import api_bp
from backend.src.QRcode_generator import gen_qrcode
from backend.src.mail_sender_SES import send_email, send_raw_email
import backend.src.db as db
from backend.src.service import user_service, user_ticket_service


def create_app():
    app = Flask(__name__, static_folder="../../frontend/static", template_folder="../../frontend/templates")
    app.register_blueprint(api_bp)
    app.config.from_object('backend.src.config.config.CONFIG')
    # app.config['APPLICATION_ROOT'] = "/mif2024/e-ticket"
    app.config['SESSION_REFRESH_ON_REDIRECT'] = True
    app.config['SESSION_REGENERATE_SAVE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_SECURE'] = True  # CONFIG.SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CONFIG.SESSION_COOKIE_SAMESITE

    app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

    # with app.app_context():
    db.init_db(app)
    db.init_ma(app)
    db.init_login_manager(app)

    # CSRFProtect(app)

    return app


app = create_app()


# @app.after_request
# def add_security_headers(resp):
#     resp.headers['Content-Security-Policy'] = "script-src 'self'"
#     return resp
# @app.route('/')
# def no():
#     return "チケット申請は終了致しました"

@app.route('/', methods=['POST'])
def home_post():
    if request.method == 'POST':
        session['form_data'] = dict(request.form)
        # logger.error(session['form_data'])

        return redirect(url_for('confirm', **request.form))


@app.route('/music-fes-2024', methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template("ticket_application_page.html")
        # return render_template("qrcode_website_form.html")
    # elif request.method == 'POST':
    #     session['form_data'] = dict(request.form)
    #     # logger.error(session['form_data'])
    #
    #     return redirect(url_for('confirm', **request.form))


@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'GET':
        # logger.error(session.get('form_data'))
        return render_template('confirmation_page.html')
    elif request.method == 'POST':
        form_data = session.get('form_data', {})
        # logger.error(form_data)
        guest_names = [form_data[f'guestName{i}'] for i in range(1, int(form_data['ticket_quantity']) + 1)]

        student_info_valid = user_service.validate_user_info(form_data['school_grades'], form_data['classes'], form_data['student_number'])
        if student_info_valid is False:
            return redirect(url_for("fail", idx=4))

        userid_dict = {}
        user_id = str(form_data['school_grades']) + str(form_data['classes']) + \
                  str(form_data['student_number']).zfill(2)

        validate_requested_ticket = user_service.validate_ticket_request(user_id, int(form_data['ticket_quantity']))
        if validate_requested_ticket['is_exist'] is False:
            logger.error('Creating new user!!')
            # privilege is initially set as "student"
            # password is initially set as None which means it cannot log in
            # username is same as user_id, so it must be changed(also passwords if set to none!).
            user_service.create_user(userid=user_id, username=user_id, first_name=form_data['first_name'],
                                     last_name=form_data['last_name'],
                                     # student_uuid=form_data['student_school_uuid'],
                                     privilege="student", password=None, email=form_data['email'],
                                     grade=form_data['school_grades'], classes=form_data['classes'],
                                     student_number=form_data['student_number'])
        if validate_requested_ticket['validation'] is True:
            current_ticket_num = validate_requested_ticket['requested_ticket_num']
            try:
                for i in range(1, 1 + int(form_data['ticket_quantity'])):
                    guest_name = guest_names[i - 1]
                    # print(form_data['school_grades'], session.get('classes'), session.get('student_number'), i)
                    # logger.debug(session.get('school_grades'), session.get('classes'), session.get('student_number'), i)

                    user_ticket_id = user_id + "_" + str(i).zfill(2)

                    output, _response_code = user_ticket_service.create_user_ticket_by_user_ticket_id(userid=user_id,
                                                                                                      ticket_id=i+current_ticket_num,
                                                                                                      invited_name=guest_name)

                    if "duplicate entry" in output['msg']:
                        if "mif24-test-ticket" in output['msg']:
                            return redirect(url_for("fail", idx=3))
                        elif "mif24-test-user.email" in output['msg']:
                            return redirect(url_for("fail", idx=4))
                        else:
                            return redirect(url_for("fail", idx=3))
                    else:
                        ticket_hash = output['result']['ticket_hash']

                    gen_qrcode(ticket_hash, guest_name, filename=user_ticket_id)

                    userid_dict[user_ticket_id] = guest_names[i - 1]

                # if "@mita-is.ed.jp" in form_data['email']:
                logger.error(userid_dict)
                send_raw_email(to=form_data['email'],
                                userid_dict=userid_dict)

                user_service.complete_ticket_request(user_id, int(form_data['ticket_quantity']))

            except Exception as e:
                logger.error(e)
                return redirect(url_for("fail", idx=1))

            return redirect(url_for("success"))
        else:
            return redirect(url_for("fail", idx=2))

@app.route('/teacher-page', methods=['GET', 'POST'])
def home_teacher():
    if request.method == 'GET':
        return render_template("ticket_application_teachers_page.html")
    elif request.method == 'POST':
        session['form_data'] = dict(request.form)
        return redirect(url_for('confirm_teacher', **request.form))

@app.route('/confirm-teacher', methods=['GET', 'POST'])
def confirm_teacher():
    if request.method == 'GET':
        # logger.error(session.get('form_data'))
        return render_template('confirmation_teachers_page.html')
    elif request.method == 'POST':
        form_data = session.get('form_data', {})
        guest_names = [form_data[f'guestName{i}'] for i in range(1, int(form_data['ticket_quantity']) + 1)]

        # student_info_valid = user_service.validate_user_info(form_data['school_grades'], form_data['classes'],
        #                                                      form_data['student_number'])
        # if student_info_valid is False:
        #     return redirect(url_for("fail", idx=4))

        userid_dict = {}
        # user_id = str(form_data['school_grades']) + str(form_data['classes']) + \
        #           str(form_data['student_number']).zfill(2)
        user_id = form_data['email'].split('@')[0]

        validate_requested_ticket = user_service.validate_ticket_request(user_id, int(form_data['ticket_quantity']))
        if validate_requested_ticket['is_exist'] is False:
            # privilege is initially set as "student"
            # password is initially set as None which means it cannot log in
            # username is same as user_id, so it must be changed(also passwords if set to none!).
            user_service.create_user(userid=user_id, username=user_id, first_name=form_data['first_name'],
                                     last_name=form_data['last_name'],
                                     # student_uuid=0000000,
                                     privilege="teacher", password=None, email=form_data['email'],
                                     grade=None, classes=None,
                                     student_number=None)
        if validate_requested_ticket['validation'] is True:
            current_ticket_num = validate_requested_ticket['requested_ticket_num']
            try:
                for i in range(1, 1 + int(form_data['ticket_quantity'])):
                    guest_name = guest_names[i - 1]
                    # print(form_data['school_grades'], session.get('classes'), session.get('student_number'), i)
                    # logger.debug(session.get('school_grades'), session.get('classes'), session.get('student_number'), i)

                    user_ticket_id = user_id + "_" + str(i).zfill(2)

                    output, _response_code = user_ticket_service.create_user_ticket_by_user_ticket_id(userid=user_id,
                                                                                                      ticket_id=i + current_ticket_num,
                                                                                                      invited_name=guest_name)

                    if "duplicate entry" in output['msg']:
                        if "mif24-test-ticket" in output['msg']:
                            return redirect(url_for("fail", idx=3))
                        elif "mif24-test-user.email" in output['msg']:
                            return redirect(url_for("fail", idx=4))
                        else:
                            return redirect(url_for("fail", idx=3))
                    else:
                        ticket_hash = output['result']['ticket_hash']

                    gen_qrcode(ticket_hash, guest_name, filename=user_ticket_id)

                    userid_dict[user_ticket_id] = guest_names[i - 1]

                # if "@mita-is.ed.jp" in form_data['email']:
                logger.error(userid_dict)
                send_raw_email(to=form_data['email'],
                               userid_dict=userid_dict)

                user_service.complete_ticket_request(user_id, int(form_data['ticket_quantity']))
            except Exception as e:
                logger.error(e)
                return redirect(url_for("fail", idx=1))

            return redirect(url_for("success"))
        else:
            return redirect(url_for("fail", idx=2))


@app.route('/fail/<int:idx>')
def fail(idx):
    messages = ["Invalid input",
                "Database Error",
                "チケットの発行上限回数に達しました。\n詳しくは" + os.environ.get('CONTACT_EMAIL', 'support@example.com') + "にお問い合わせください。",
                "Ticket information already exists in the database - duplicate entry",
                "存在しない生徒情報でチケットが申請されました。\n恐れ入りますが、入力された生徒情報が正しい事を今一度お確かめ下さい。",
                "お使いになった生徒情報が既に他の生徒に使用されたか、ご入力頂いた情報に誤りがある可能性があります。\n恐れ入りますが、生徒情報が正しいことをご確認の上、" + os.environ.get('CONTACT_EMAIL', 'support@example.com') + "にお問い合わせ下さい。\nご協力をお願い致します。",
                "SERVER ERROR"]
    return render_template("fail.html", message=messages[idx])


@app.route('/success', methods=['GET'])
def success():
    return render_template("success.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        return user_service.login(name, email, password)

    if request.method == 'GET':
        return render_template('admin/login.html')


@app.route('/admin/mif_admin')
@login_required
def mif_admin():
    # todo view ticket usage count
    # todo require password or some kind of authentication to view this page
    return render_template("admin/mifadmin.html")


@app.route('/admin/xiao_admin')
@login_required
def xiao_admin():
    # todo view database
    # todo require password or some kind of authentication to view this page
    # todo restore ticket usage
    # todo toggle day 1 and day 2
    # 参考：https://qiita.com/Bashi50/items/e3459ca2a4661ce5dac6
    return render_template("admin/xiao_admin.html")


# @app.route('/admin/recreate_db/force')
# def _reset_db():
#     with app.app_context():
#         db.db.drop_all()
#         db.db.create_all()


if __name__ == '__main__':
    # # logger.error(user_service.verify_request_ticket("S2E12", 1))
    # with app.app_context():
    #     db.db.drop_all()
    #     db.db.create_all()
    #     print("Database created")
    # user = user_service.create_user(userid="S2E12", username="admin", first_name="Sota", last_name="Kobayashi", student_uuid=1234567,
    #                                 privilege="admin", password="Xaolin1324",
    #                                 email="example@example.com",
    #                                 grade=5, classes="E", student_number=12)
    # add_user_ticket_to_db(username='S2E1201', user_hash='',invited_name='Sota Kobayashi 1st')
    # export_database(app)

    app.run(debug=True, port=5000)
    # with app.app_context():
    #     db.db.drop_all()
    #     db.db.create_all()
    #     db.add_user_ticket_to_db(user_ticket_id='S2E1201', user_hash='lol', invited_name='Sota Kobayashi 1st')
