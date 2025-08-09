import shutil
from backend.src.config.config import *

import qrcode
from PIL import Image, ImageDraw, ImageFont


def gen_qrcode(ticket_hash, guest_name, filename, box_size=10) -> None:
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=4
    )
    qr.add_data(ticket_hash)
    qr_img = qr.make_image(fill_color="black", back_color=(254, 232, 200)).resize(size=(TICKET_METADATA['qr_size'], TICKET_METADATA['qr_size']))
    ticket_template = Image.open(TICKET_TEMPLATE)
    output_img = ticket_template.copy()
    output_img.paste(qr_img, (TICKET_METADATA['qr_x'], TICKET_METADATA['qr_y']))

    draw = ImageDraw.Draw(output_img)
    try:
        font = ImageFont.truetype("frontend/static/fonts/NotoSans.ttf", TICKET_METADATA['font_size'])
    except Exception as e:
        font = ImageFont.truetype("../../frontend/static/fonts/NotoSans.ttf", TICKET_METADATA['font_size'])

    draw.text((TICKET_METADATA['name_text_x'], TICKET_METADATA['name_text_y']), guest_name, fill="black", anchor='mm', font=font)
    # テスト用の文字を挿入する
    # draw.text((TICKET_METADATA['name_text_x'], TICKET_METADATA['name_text_y']*1.2), "テスト用", fill="red", anchor='mm',
    #           font=font)

    #png
    # output_img.save(OUTPUT_TICKET_DIR + filename + ".png")

    #jpg
    output_img = output_img.convert("RGB")
    output_img.save(OUTPUT_TICKET_DIR + filename + ".jpg", "JPEG")

    qr.clear()

    # img.show()
    return None


def _clear_output_folders():
    if input("Are you sure to delete all files in the output ticket folder? (y/n): ") == "y":
        shutil.rmtree(OUTPUT_TICKET_DIR)
        os.mkdir(OUTPUT_TICKET_DIR)


if __name__ == "__main__":
    # _clear_output_folders()
    # time.sleep(5)
    print(convert_username_to_hash("S1D2401"))
    gen_qrcode(ticket_hash=convert_username_to_hash("S1D2401"), guest_name="田中様", filename="S1D24_01")
    # gen_qrcode(ticket_hash=convert_username_to_hash("S2E1202"), guest_name="g2", filename="S2E12_02")
    # gen_qrcode(ticket_hash=convert_username_to_hash("J1F3702"), guest_name="森山　大", filename="J1F37_02")
    # gen_qrcode(ticket_hash=convert_username_to_hash("J1F3703"), guest_name="森山　夏帆", filename="J1F37_03")
    # gen_qrcode(ticket_hash=convert_username_to_hash("J1F3704"), guest_name="神田　悠衣", filename="J1F37_04")
    # gen_qrcode(ticket_hash=convert_username_to_hash("J1F3705"), guest_name="岡　芽那", filename="J1F37_05")
    # gen_qrcode(ticket_hash=convert_username_to_hash("J1F3706"), guest_name="菊地　冬聖", filename="J1F37_06")
    # gen_qrcode(ticket_hash=convert_username_to_hash("J1F3707"), guest_name="豊　幸乃介", filename="J1F37_07")
    # gen_qrcode(ticket_hash=convert_username_to_hash("J1F3708"), guest_name="窪田　優樹", filename="J1F37_08")
    # gen_qrcode(ticket_hash=convert_username_to_hash("J1F3709"), guest_name="広瀬　柊人", filename="J1F37_09")

    print("Done")
