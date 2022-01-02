import smtplib
import ssl
from datetime import datetime, timedelta
import gspread
from flask import Flask
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')                        # smtp server credentials

app = Flask(__name__)

status_list = ["Applied",
               "Online Test Sent",
               "Reminder Sent",
               "Submitted Test",
               "Interview Mail Sent",
               "Refusal Mail Sent"
               ]


def send_email(email_destination, message_type, project_name):    # send emails get the
    port = 465
    smtp_server_domain_name = "smtp.gmail.com"
    sender_mail = config.get('main', 'sender_mail')
    password = config.get('main', 'password')

    email_destination = email_destination
    if sender_mail.endswith("@datagram.ai"):
        if message_type == "Online Test Sent":
            message = "Thank you for applying to ", project_name, "."
        elif message_type == "Reminder Sent":
            message = "You haven’t submitted your test. Everything okay?"
        elif message_type == "Refusal Mail Sent":
            message = "We are sorry to tell you that you did not pass the test"
        elif message_type == "Interview Mail Sent":
            message = "Congratulations for passing the test. You’ll have an interview with _____"

        ssl_context = ssl.create_default_context()
        service = smtplib.SMTP_SSL(smtp_server_domain_name, port, context=ssl_context)
        service.login(sender_mail, password)

        service.sendmail(sender_mail, email_destination, f"Subject: PFE Application Update\n{message}")

        service.quit()

    else:
        print("bad email")


def check_7_days_olds(old_date):                           # to verify the email sent is 7 days old
    oo = old_date.split(" ")[0].split("/")
    past = datetime(int(oo[2]), int(oo[1]), int(oo[0]))
    present = datetime.now() - timedelta(days=7)
    return past < present


@app.route('/')
def pipeline_flask():
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
            elif item[3] == "Applied":
                wks.update_cell(x, 4, 'Online Test Sent')
                wks.update_cell(x, 5, datetime_object)
                send_email(item[1], "Online Test Sent", item[2])
                break
            elif item[3] == "Online Test Sent" and not check_7_days_olds(item[4]) and not item[5]:
                wks.update_cell(x, 4, 'Reminder Sent')
                wks.update_cell(x, 5, datetime_object)
                send_email(item[1], "Reminder Sent")
                break
            elif item[3] == "Submitted Test" and eval(item[5]) < 0.5:
                wks.update_cell(x, 4, 'Refusal Mail Sent')
                wks.update_cell(x, 5, datetime_object)
                send_email(item[1], "Refusal Mail Sent")
                break
            elif item[3] == "Submitted Test" and eval(item[5]) > 0.5:
                wks.update_cell(x, 4, 'Interview Mail Sent')
                wks.update_cell(x, 5, datetime_object)
                send_email(item[1], "Interview Mail Sent")
        return 'everything is working fine!'
    except Exception:
        return 'something went very wrong the data is probably mess!, it\'s our fault'


if __name__ == '__main__':
    app.run()
