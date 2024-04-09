import requests
import os
from csv_methods import get_data_from_csv, create_csv
from analytics import error 
from analytics import logger

def open_key(file_path):
    with open(file_path, 'r') as file:
        key = file.read()
    return key

BASE_URL = "https://server.smartlead.ai/api/v1"
API_KEY = open_key("/home/ubuntu/app/main/keys/key_smartlead.txt")

def all_email_accounts():
    logger.info("Getting all emails")
    url = BASE_URL + f"/email-accounts/?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None
    # returns a list
    return response.json()

def all_campaigns():
    logger.info("Getting all campaigns")
    url = BASE_URL + f"/campaigns?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None
    return response.json()


def create_campaign(name):
    logger.info("Creating campaign")
    url = BASE_URL + f"/campaigns/create/?api_key={API_KEY}"
    data = {"name": name}
    response = requests.post(url, data=data)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None
    
    response = response.json()
    return response["id"], response["created_at"]

def all_email_from_campaign(campaign_id):
    logger.info("Getting all emails from campaign")
    url = BASE_URL + f"/campaigns/{campaign_id}/email-accounts?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        logger.info(f"error making request: {response.status_code}, {response.text}")
        return None
    else:
        return response.json()

def add_email(camp, mails):
    logger.info("adding emails")
    url = BASE_URL + f"/campaigns/{camp}/email-accounts?api_key={API_KEY}"
    data = {"email_account_ids": [mails]}
    response = requests.post(url=url, data=data)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None

def delete_email(campaign_id, email_ids):
    logger.info("deleting emails")
    url = BASE_URL + f"/campaigns/{campaign_id}/email-accounts?api_key={API_KEY}"
    data = {"email_account_ids": email_ids}
    response = requests.delete(url=url, data=data)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None


def enable_warmup(email_id):
    logger.info("Enable warmup")
    url = BASE_URL + f"/email-accounts/{email_id}/warmup?api_key={API_KEY}"
    data = {
            "warmup_enabled": True,
            "total_warmup_per_day": 20,
            "daily_rampup": 2,
            "reply_rate_percentage": 38
        }
    response = requests.post(url=url, data=data)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None

def update_email(email_id, rampup = 0):
    logger.info("Change email settings")
    url = BASE_URL + f"/email-accounts/{email_id}?api_key={API_KEY}"
    data = {
        "max_email_per_day": 15 + rampup
    }
    response = requests.post(url=url, data=data)    
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None
    
def set_campaign_settings(campaign_id):
    logger.info("Updataing settings for campaign")
    url = BASE_URL + f"/campaigns/{campaign_id}/settings?api_key={API_KEY}"
    data = {
        "stop_lead_settings": "REPLY_TO_AN_EMAIL",
        "send_as_plain_text": False,
        "follow_up_percentage": 100
    }
    response = requests.post(url=url, data=data)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None

def set_campaign_schedule(campaign_id):
    logger.info("Setting campaign schedule")
    url = BASE_URL + f"/campaigns/{campaign_id}/schedule?api_key={API_KEY}"
    data = {
    "timezone": "America/New_York",
    "days_of_the_week": [1,2,3,4,5],  
    "start_hour": "06:00",        
    "end_hour": "17:00",      
    "min_time_btw_emails": 7, 
    "max_new_leads_per_day": 75 
    }
    response = requests.post(url=url, data=data)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None

def add_leads(campaign_id, creator, max_leads):
    logger.info("Adding leads to campaign")
    # Check if user has a csv
    # specify the directory to search in
    dir_path = "/home/ubuntu/app/main/csv"

    # specify the file path to check for
    file_path = os.path.join(dir_path, f'{creator.creator_domain}.csv')

    # check if the file exists within the directory
    if os.path.exists(dir_path) and os.path.exists(file_path) and os.path.isfile(file_path):
        logger.info(f"Creator has their own csv, grabbing data...")
    
    # If user does not have a csv then generate csv
    else:
        logger.info(f"Creator does not have their own csv at {dir_path}, creating csv")
        create_csv(creator)
    
    leads_list = get_data_from_csv(file_path, creator, max_leads)
    if leads_list == None:
        logger.critical(f"Adding no leads, critical error. creator: {creator.creator_domain}")
        error(f"critical error uploading leads to creator campaign ({creator.creator_domain}). Didn't upload anything.")
    
    url = BASE_URL + f"/campaigns/{campaign_id}/leads?api_key={API_KEY}"
    data_list = list()
    total_leads = 0
 
    for lead in leads_list:
        data = {
            "first_name": lead.firstname,
            "last_name": lead.lastname,
            "email": lead.email,
            "phone_number": "0",
            "company_name": lead.company,
            "website": lead.website,
            "location": lead.location,
            "custom_fields": {
                "name": lead.firstname + " " + lead.lastname,
                "title": lead.position,
                "body":  lead.cold_mail_body,
                "follow_1": lead.follow_ups[0],
                "follow_2": lead.follow_ups[1],
                "follow_3": lead.follow_ups[2],
                "follow_4": lead.follow_ups[3]
                }, 
            "linkedin_profile": lead.linkedin,
            "company_url": lead.website
        }
        data_list.append(data)

    settings = {
        "ignore_global_block_list": True,
        "ignore_unsubscribe_list": True,
        "ignore_duplicate_leads_in_other_campaign": False
    }
    json_data = {
        "lead_list": data_list,
        "settings": settings
    }
    response = requests.post(url=url, json=json_data)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error¨ making request: {response.status_code}, {response.text}")
        return None

    response_data = response.json()
    total_leads += int(response_data["total_leads"])
    logger.info(f"Info from inserting leads into smartleads for campaign: {creator.creator_domain}, Number of leads added: {total_leads}")

    if total_leads < max_leads:
        # Adding more leads
        del leads_list
        del data_list
        return total_leads
    
    # TODO, If not enough leads in custom csv then add leads from master csv
    del leads_list
    del data_list
    return ""

def get_all_leads(campaign_id, offset=0, limit=210):    
    url = BASE_URL + f"/campaigns/{campaign_id}/leads?api_key={API_KEY}&offset={offset}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        logger.info(f"Error fetching leads from campaign: {response.json()}")
        return None
    return response.json()
    
def create_sequence(campaign_id):
    logger.info("Creating email sequence")
    url = BASE_URL + f"/campaigns/{campaign_id}/sequences?api_key={API_KEY}"
    data = {
        "sequences": [
        {
        "seq_number": 1,
        "seq_delay_details":{
            "delay_in_days":3
        }, 
        "subject": "Information for {{name}}",
        "email_body": "{{body}}"  
        },
        {
        "seq_number": 2,
        "seq_delay_details": {
            "delay_in_days": 4
        },
        "subject": "Information for {{name}}",
        "email_body": "{{follow_1}}"
        },
        {
        "seq_number": 3,
        "seq_delay_details": {
            "delay_in_days": 4
        },
        "subject": "Information for {{name}}",
        "email_body": "{{follow_2}}"
        },
        {
        "seq_number": 4,
        "seq_delay_details": {
            "delay_in_days": 4
        },
        "subject": "Information for {{name}}",
        "email_body": "{{follow_3}}"
        },
        {
        "seq_number": 5,
        "seq_delay_details": {
            "delay_in_days": 4
        },
        "subject": "Information {{name}}",
        "email_body": "{{follow_4}}"
        }]
    }
    response = requests.post(url=url, json=data)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None

def get_seq(campaign_id):
    url = BASE_URL + f"/campaigns/{campaign_id}/sequences?api_key={API_KEY}"
    response = requests.get(url)
    logger.info(response.text)


def launch_campaign(campaign_id):
    logger.info("Lanching campaign")
    url = BASE_URL + f"/campaigns/{campaign_id}/status?api_key={API_KEY}"
    data = {"status": "START"}
    response = requests.post(url=url, data=data)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None

def get_analytics(campaign_id, start, end):
    url = BASE_URL + f"/campaigns/{campaign_id}/analytics-by-date?api_key={API_KEY}&start_date={start}&end_date={end}"
    response = requests.get(url=url)
    if response.status_code != 200:
        logger.error(f"error making request: {response.status_code}, {response.text}")
        error(f"error making request: {response.status_code}, {response.text}")
        return None
    return response.json()