from flask import Flask
import gspread
import smtplib
from datetime import datetime, timedelta

app = Flask(__name__)

status_list = ["Applied",
               "Online Test Sent",
               "Reminder Sent",
               "Submitted Test",
               "Interview Mail Sent",
               "Refusal Mail Sent"
               ]


def send_email(email_destination):
    sender = 'elyes@datagram.ai'
    email_destination = email_destination

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    This is a test e-mail message.
    """


def check_7_days_olds(old_date):
    oo = old_date.split(" ")[0].split("/")
    past = datetime(int(oo[2]), int(oo[1]), int(oo[0]))
    present = datetime.now() - timedelta(days=7)
    return past < present


@app.route('/')
def hello_world():
    try:
        cr = gspread.service_account(filename="credentials.json")
        sh = cr.open("Pipeline")
        wks = sh.worksheet("Candidates")
    except gspread.exceptions.GSpreadException:
        return "connection fails"
    try:
        x = 1
        for item in wks.get_all_values()[1:]:
            x = x + 1
            datetime_object = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if item[3] not in status_list:
                print("mess info")
                break
            if item[3] == "Applied":
                wks.update_cell(x, 4, 'Online Test Sent')
                wks.update_cell(x, 5, datetime_object)
                send_email(item[1], "Online Test Sent")
                print(check_7_days_olds(datetime_object))
                break
            if item[3] == "Online Test Sent" and not check_7_days_olds(item[4]) and not item[5]:
                wks.update_cell(x, 4, 'Reminder Sent')
                wks.update_cell(x, 5, datetime_object)
                send_email(item[1], "Reminder Sent")
                print(check_7_days_olds(datetime_object))
                break
            if item[3] == "Submitted Test" and eval(item[5]) < 0.5:
                wks.update_cell(x, 4, 'Refusal Mail Sent')
                wks.update_cell(x, 5, datetime_object)
                send_email(item[1], "Refusal Mail Sent")
                print(check_7_days_olds(datetime_object))
                break
            if item[3] == "Submitted Test" and eval(item[5]) > 0.5:
                wks.update_cell(x, 4, 'Interview Mail Sent')
                wks.update_cell(x, 5, datetime_object)
                send_email(item[1], "Interview Mail Sent")
                print(check_7_days_olds(datetime_object))
        return 'everything is working fine!'
    except Exception:
        return 'something went very wrong the data is probably mess!, it\'s our fault'


if __name__ == '__main__':
    app.run()
