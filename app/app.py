from flask import Flask, request
from twilio.rest import Client
from multiprocessing import Process
import time
import logging as log
from datetime import datetime

# create a logger object
logger = log.getLogger('logger')
# set the log level
logger.setLevel(log.DEBUG)
# create a console handler
console_handler = log.StreamHandler()
now = datetime.now()
date_string = now.strftime("%d-%m-%Y")
file_handler = log.FileHandler(f"/home/ubuntu/app/onboarding/logs/{date_string}.txt")
console_handler.setLevel(log.DEBUG)
file_handler.setLevel(log.DEBUG)
# create a formatter
formatter = log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s \n')
# add the formatter to the console handler
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
# add the console handler to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Variables
account_sid = "AC1af9b8d48c4d02567e1f1a7e5fbff65a"
auth_token = "c946393ce8dbd7e10f4b6a692e135c30"
abs_num = "+13203613517"
abs_whatsapp = "whatsapp:" + abs_num
delay = 3
handlers = ["whatsapp:+46761016185", "whatsapp:+46725643210"] # 0: Tiger, 1: Jonathan 

client = Client(account_sid, auth_token)
app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def receive_sms():
    #get incoming message
    message_body = request.values.get('Body')
    check = message_body.replace(" ", "").lower()
    Client_num = request.values.get("From")
    From_num = request.values.get("To")
    logger.info(f"Received message: {message_body} \nFrom: {Client_num}")
    p = Process(target=processing_msg, args=(From_num, Client_num, message_body, check))
    p.start()
    return "ok"

def processing_msg(From_num, client_num, msg_body, check):
    try:
        if check == "startonboarding":
            # Response first message:
            body = "Thank you so much for signing up to Honeypot!\n\nWe're thrilled to have you on board and look forward to helping you find the perfect collaborations."
            send_response(body, client_num, From_num)
            time.sleep(delay)

            body = '''Our onboarding process only takes about 15-25 mins, and once you're done, you can just relax and wait for opportunities to come your way! 🚀

    Here's the link: https://honeypotsocial.com/onboarding

    If you need any assistance, you can reach support through this SMS chat by typing "support:" followed by your question or by sending us an email at support@honeypotemail.com

    We're here to help!'''

            send_response(body, client_num, From_num)
            time.sleep(delay)

            body = '''Hey there! As we're getting your account ready, could you lend us a hand? It'll take just 3 minutes of your time to fill out this survey: https://forms.gle/1ZpQt2tzbi8TZcXA8.

    By sharing your onboarding experience, you're helping us make the journey smoother for everyone. Thanks a bunch for being with us on this adventure!'''
            send_response(body, client_num, From_num)
            time.sleep(delay)

            body = '''Once you finish the onboarding process, kindly send us a confirmation message with only the word 'done' to let us know that you've finished the onboarding.

    Thank you for choosing our Honeypot, and we look forward to working with you!'''
            send_response(body, client_num, From_num)

        elif check == "done":
            # Response to finished msg
            body = '''Thanks for confirming that you're all set with onboarding! We appreciate your help in making the process smooth.

    Just wanted to give you a heads up that setting up your account will take around 48-72 hours. We need to configure MX, SPF, DKIM, and forwarding to make sure that your emails don't end up in spam.

    If you have any questions, feel free to reach out to us by sending a message which starts with 'support:' followed by the problem or at support@honeypotemail.com.

    As soon as everything is good to go, we'll let you know. In the meantime, don't hesitate to contact us if you need any assistance.

    Thanks for choosing us, and we're excited to work with you!
    '''
            send_response(body, client_num, From_num)
            send_client_got(client_num)

        elif "admin-send" in check:
            message = msg_body.split(",")
            client_num = message[1]
            body = message[2]
            sms = message[3].lower().replace(" ", "")
            if sms == "whatsapp":
                send_response(body, client_num, abs_whatsapp)
            else:
                send_response(body, client_num, abs_num)

        elif "support:" in msg_body.lower():
            body = f''' Thanks for reaching out to our support team!
    Your message has been forwarded and we will get in touch with you as soon as possible. In the mean time don't hesitate to also reach out through our email at: support@honeypotemail.com

    Thank you so much for singing up for our service and for your patience!

    Kind regards,
    Support staff at Honeypot socials
    '''

            send_response(body, client_num, From_num)

            body = f"Support message from {client_num}: \n\n {msg_body}"
            for handler in handlers:
                if "whatsapp:" in handler:
                    send_response(body, handler, abs_whatsapp)
                else:
                    send_response(body, handler, abs_num)
                
        else:
            # Response to unhandled message, sending message to Tiger
            body = f'''Sorry! 
    There was a problem with your earlier message,

    If you're trying to start onboarding, send the message 'start onboarding' 
    If you're done with the onboarding please send 'done'. 
    If you're trying to reach support please start your message with "support:" followed by a description of your problem and any necessary details.

    Thanks in advance for your understanding!
    '''
            send_response(body, client_num, From_num)

            body = f"Message from:{client_num}\n\n Response unhandled: {msg_body}"
            for handler in handlers:
                if "whatsapp:" in handler:
                    send_response(body, handler, abs_whatsapp)
                else:
                    send_response(body, handler, abs_num)
    except Exception as e:
         error(e, client_num, msg_body)

def send_response(msg_body, client_number, sender):
	message = client.messages.create(to=client_number, from_=sender, body=msg_body)
	logger.info("Message sent to: " + client_number + " with the body: " + msg_body)

def send_client_got(client_num):
    body = f"Client sent finish message: {client_num}"
    for handler in handlers:
        if "whatsapp:" in handler:
            send_response(body, handler, abs_whatsapp)
        else:
            send_response(body, handler, abs_num)

def error(error, client_num, message):
     body = f'''Error occured: {error}\nMessage from: {client_num} -- {message} '''
     logger.error(body)
     for handler in handlers:
        if "whatsapp:" in handler:
            send_response(body, handler, abs_whatsapp)
        else:
            send_response(body, handler, abs_num)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080)