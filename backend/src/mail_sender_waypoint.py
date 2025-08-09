import requests
import base64
import os
from config.config import WAYPOINT_API_UNAME, WAYPOINT_API_PASS, logger

# Endpoint URL
url = "https://live.waypointapi.com/v1/email_messages"

# Headers
headers = {
    "Content-Type": "application/json",
}
auth = {
    "username": WAYPOINT_API_UNAME,
    "password": WAYPOINT_API_PASS
}

files = {
    '1': ('Sota.png', open('Sota.png', 'rb')),
}

def encode_file(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode()

def send_email(to: str, user_name, userid_list):
    img_html = ""
    e_ticket_base_path = f"cid:backend/outputs/output_ticket/"
    e_ticket_path_list = [e_ticket_base_path + userid + '.png' for userid in userid_list]
    for ticket_path in e_ticket_path_list:
        print(ticket_path)
        img_html += f'<img src="{ticket_path}">'
    print(e_ticket_path_list)

    # Email data
    data = {
        "templateId": "wptemplate_pHhBpX2HGbzLPL1j",
        "to": to,
        "variables": {
            "user_name": user_name,
            "image": "<img src='cid:Sota.png'>"
        },

    }

    # Make POST request
    response = requests.post(url, json=data, headers=headers, auth=(auth["username"], auth["password"]))

    # Check response
    if response.status_code == 201:
        print("Email sent successfully!")
        print("Response:", response.json())
    else:
        print("Failed to send email.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        logger.error(response.text)


body = f"[返信不可]\
    \nこの度はチケット申請フォームにご回答いただきありがとうございます。\
    \n\n イベントの詳細については、こちらのリンクを御覧下さい：www.MIF2024.com\
    \n\n 招待したい人にチケットの画像を共有してください。\n当日は、添付の電子チケットを受付に提示してください。\
    \nご不明な点がございましたら、お気軽にお問い合わせください:\n" + os.environ.get('CONTACT_EMAIL', 'support@example.com') + "。\
    \n\n\n\nXiaolin's TechClub 2024"


def send_raw_email(to: str, user_name, userid_list):
    global body
    img_html = ""
    e_ticket_base_path = f"cid:backend/outputs/output_ticket/"
    e_ticket_path_list = [e_ticket_base_path + userid + '.png' for userid in userid_list]
    for ticket_path in e_ticket_path_list:
        print(ticket_path)
        img_html += f'<img src="{ticket_path}">'
    print(e_ticket_path_list)

    # Email data
    data = {
        "to": to,
        "from": os.environ.get('FROM_EMAIL', 'noreply@example.com'),
        "subject": "MIF電子チケット応募フォームへのご回答ありがとうございます。",
        # "bodyHtml": f'<html><body><p>{body}</p>{img_html}</body></html>',
        "bodyHtml": f'<html><body><p>hello</p><p><img src="cid:Sota.png"></p></body></html>',

    }

    # Make POST request
    response = requests.post(url, json=data, headers=headers, auth=(auth["username"], auth["password"]))

    # Check response
    if response.status_code == 201:
        print("Email sent successfully!")
        print("Response:", response.json())
    else:
        print("Failed to send email.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        logger.error(response.text)

if __name__ == '__main__':
    send_email("example@example.com", "TestUser", ["Test1", "Test2"])
    # send_raw_email("example@example.com", "TestUser", ["Test1"])
