from dotenv import load_dotenv
from backend.src.config.config import EVENT_NAME_IN_MAIL
import boto3
import os

from backend.src.config.config import ROOT_DIR, logger

load_dotenv()

# \n\n 招待したい人にスクリーンショット等でメールに添付されたチケット画像を共有してください。トラブル防止のために、チケットの送信先を間違えないようにしてください。\

body = f"[返信不可]\
    \nこちらのメールは返信不可となっております。\
    \n\n{EVENT_NAME_IN_MAIL}当日は、添付の電子チケットを受付に提示してください。\
    \n\nご不明な点がございましたら、下記メールアドレスにお問い合わせください:\n\" + os.environ.get('CONTACT_EMAIL', 'support@example.com') + \"。\
    \n\n\n\nXiaolin's TechClub 2024"


def send_email(to, userid_list, source=None):
    if source is None:
        source = os.environ.get('FROM_EMAIL', 'noreply@example.com')
    global body
    img_html = ""
    client = boto3.client('ses', region_name='ap-northeast-1')  # リージョン
    e_ticket_base_path = f"cid:backend/outputs/output_ticket/"
    e_ticket_path_list = [e_ticket_base_path + userid + '.jpg' for userid in userid_list]
    for ticket_path in e_ticket_path_list:
        print(ticket_path)
        img_html += f'<img src="{ticket_path}">'
    print(e_ticket_path_list)

    response = client.send_email(
        Destination={
            'ToAddresses': [to]
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': body
                },
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': f'<html><body><p>{body}</p>{img_html}</body></html>'
                    # 'Data': f'<html><body><p>hello</p><p><img src="cid:Sota.png"></p></body></html>'
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': f"{EVENT_NAME_IN_MAIL}電子チケット応募フォームへのご回答ありがとうございます。"
            }
        },
        Source=source
    )
    return response


# 環境変数が正しく設定されてるか確認
# print("AWS_ACCESS_KEY_ID:", os.getenv("AWS_ACCESS_KEY_ID"))
# print("AWS_SECRET_ACCESS_KEY:", os.getenv("AWS_SECRET_ACCESS_KEY"))
# print("AWS_DEFAULT_REGION:", os.getenv("AWS_DEFAULT_REGION"))


import json

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import boto3
from botocore.exceptions import ClientError

os.environ['TZ'] = 'Asia/Tokyo'
SRC_MAIL = os.environ.get('FROM_EMAIL', 'noreply@example.com')
# DST_MAIL = 'to@test.email'
SES_REGION = "ap-northeast-1"
ses = boto3.client('ses', region_name=SES_REGION)


# s3 = boto3.resource('s3')
# BUCKET_NAME = 'attached_file_store'
# bucket = s3.Bucket(BUCKET_NAME)

# from a file path, extract the base name of the file
# i.e. t.akazawa_01.jpg -> t.akazawa_01
# i.e. S2E12_01.jpg     -> S2E12_01
def _extract_base_name_from_filename(filename):
    parts = filename.split('.')
    return '.'.join(parts[:-1]) if len(parts) > 1 else filename

def send_raw_email(to, userid_dict):
    logger.info('send_raw_email: START')
    e_ticket_base_path = "backend/outputs/output_ticket/"
    # e_ticket_base_path = "../outputs/output_ticket/"
    e_ticket_path_list = [e_ticket_base_path + userid + '.jpg' for userid in userid_dict.keys()]

    msg = MIMEMultipart()

    msg['Subject'] = f"{EVENT_NAME_IN_MAIL}電子チケット申請フォームへのご回答ありがとうございます。"
    msg['From'] = SRC_MAIL
    msg['To'] = to
    body_msg = MIMEText(body, 'plain')
    msg.attach(body_msg)

    for img_path in e_ticket_path_list:
        print("img_path", img_path)
        att = MIMEApplication(open(img_path, 'rb').read())
        # filename shown in gmail
        base_filename = _extract_base_name_from_filename(img_path.split('/')[-1])
        # filename is replaced with guest name
        filename = userid_dict[base_filename]+'.jpg'
        print("filename:", filename)
        att.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(att)

    try:
        response = ses.send_raw_email(
            Source=SRC_MAIL,
            Destinations=[to],
            RawMessage={
                'Data': msg.as_string()
            }
        )
        return response

    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        # else:
        # LOGGER.info("Email sent! Message ID:"),
        # LOGGER.info(response['MessageId'])




if __name__ == "__main__":
    # 試し
    # send_email(
    #     source="noreply@example.com",
    #     to="example@example.com",
    #     # qrcode_path=ROOT_DIR+"backend/outputs/output_ticket/Sota.png"
    #     userid_list=["Sota"]
    # )
    os.chdir("../../")
    print(os.getcwd())

    output = send_raw_email(
        to="example@example.com",
        userid_dict={"t.akazawa_01":"guest1"}
    )
    print(output)
