from twilio.rest import Client
import openai
from datetime import datetime
import logging as log


    # create a logger object
logger = log.getLogger('logger')

# set the log level
logger.setLevel(log.DEBUG)

# create a console handler
console_handler = log.StreamHandler()
now = datetime.now()
date_string = now.strftime("%d-%m-%Y")

file_handler = log.FileHandler(f"/home/ubuntu/app/main/logs/{date_string}.txt")

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
# Your Twilio account SID and Auth Token
def open_key(file_path):
    with open(file_path, 'r') as file:
        key = file.readlines()
    for i, k in enumerate(key):
        key[i] = k.replace("\n", "")
    return key

twilio_keys = open_key("/home/ubuntu/app/main/keys/key_twilio.txt")
openai_key = open_key("/home/ubuntu/app/main/keys/key_openai_2.txt")

# Your Twilio phone number
abs_num = "+13203613517"
abs_whatsapp = "whatsapp:"+abs_num

# Handler (manual error receiver)
handler = ["+46761016185"] # Add Jonathans number when production ready: "+46725643210", change my number to whatsapp

# Create a Twilio client
client = Client(twilio_keys[0], twilio_keys[1])

def send_message(from_number, to_number, body):
    # Send the message
    client.messages.create(
        to=to_number,
        from_=from_number,
        body=body
    )

    logger.info(f"Message sent to {to_number}, from {from_number}, with the body: {body}")

def get_body(name, total, read, replies):
    openai.api_key = openai_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.4,
        messages=[
               {"role": "system", "content": "You are an agent that helps us convey information to our client's outreach about how the campaign is performing too our clients.  Your job will be to convey the data we give you and write a nice message that helps our clients understand the data.\n \
                                            If the data includes zero replies write an encouraging message to the client with a funny twist.\n \
                                            If the data includes one or more replies congratulate them on the success of their email campaign and make it a funny and relaxed message.\n \
                                            Your first message will be our data that you will use to write the sms that we will send to our client."},

               {"role": "user", "content": f"Make a sms message with this data included in it: Name: {name}, emails sent: {total}, emails read: {read}, emails replies: {replies}, sender name: Honeypot"}
               ]
    )
    return response['choices'][0]['message']['content']
    
    
def main(name, total_sent, emails_read, replies, phone, sms):
    message = get_body(name, total_sent, emails_read, replies)

    if "sms" == sms:  
        logger.info(f"Got information and sending message SMS")
        send_message(abs_num, phone, message)

    elif "whatsapp" == sms:
        logger.info(f"Got information and sending message WHATSAPP")
        send_message(abs_whatsapp, phone, message)
    else:
        #TODO Add error in sending message and send using default 
        pass
def error(message):
    # Sending error for manual fix
    logger.critical(f"Would send message: {message} to handler")
    #for hand in handler:
    #    send_message(abs_num, hand, message)

def send_confirmation(creator):
    body = f'''Great news {creator.creator_name}! Everything is now set up for {creator.creator_domain}, and we'll start sending emails for you today. 

To avoid landing in spam, we'll begin by sending 15 emails per Google Workspace user per day. Each week, we'll increase this number by 5 until we reach our goal of 35 emails per day per user. It will take about one month until we can send at full capacity.

We highly recommend that you check your email inbox at least once a day. The faster you can respond to an interested prospect, the higher the likelihood that you'll end up working together.

Thank you for taking the time to invest in yourself, and we're thrilled to help you on this journey. 

If you have any questions or need assistance, feel free to reach out. We're excited to work with you!'''

    if creator.creator_sms == "sms":
        send_message(abs_num, creator.creator_phone, body)
    elif creator.creator_sms == "whatsapp":
        send_message(abs_whatsapp, creator.creator_phone, body)
    else:
        #TODO Add error when sending message and send using default
        pass

if __name__ == "__main__":
    error("Hello")