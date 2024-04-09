from api_methods import all_campaigns, all_email_accounts, all_email_from_campaign # Getting info
from api_methods import add_email, add_leads, get_all_leads # Leads and emails
from api_methods import create_campaign, create_sequence # Creation
from api_methods import enable_warmup, update_email, get_seq, get_analytics # Settings and checks
from api_methods import set_campaign_schedule, set_campaign_settings, launch_campaign # campaign settings and Launch

from google_methods import get_gspread, add_data_to_gspread, increase_week, increase_month
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import traceback
from analytics import logger
from analytics import error, main, send_confirmation
from upload_logs import upload_file_to_folder
import math as m

def add_creator_to_obj():    
    values = get_gspread()
    if values == None:
        # This is worse case, cannot get creators from the google spread sheet.
        return None
    
    object_list = list()
    for item in values:
        if item[1] == "":
            continue
        campaign_id = item[-4]
        creation = item[-3]
        month = item[-2]
        week = item[-1]
        plan = item[8]
        if plan == '':
            plan = 0

        if campaign_id == "":

            object_list.append(
                Creator(creator_domain=item[7], creator_name=item[1], creator_phone=item[2], creator_sms=item[3], plan=plan,
                        pref_country=item[4], pref_size=item[5], pref_industry=item[6]))
        else:
            object_list.append(
                Creator(campaign_id=campaign_id, plan=plan, creation=creation, month=month, week=week,
                        creator_domain=item[7], creator_name=item[1], creator_phone=item[2], creator_sms=item[3], 
                        pref_country=item[4], pref_size=item[5], pref_industry=item[6])
        )
    return object_list

def get_email_domains():
    # Extract email domains and campaign names
    emails = all_email_accounts()
    if emails == None:
        # Failed making api request to Smartleads api
        return None
    email_dict = {}
    domain_list = list()
    for email in emails:
        id = email["id"]
        domain = email['from_email'].split("@")[1].lower()
        domain_list.append(domain.lower())
        if domain in email_dict:
            email_dict[domain].append(id)
        else:
            email_dict[domain] = [id]

    return domain_list, email_dict

def get_campaign_names():
    campaign_list = all_campaigns()
    c_names = list()
    c_ids = list()
    for camp in campaign_list:
        c_names.append(camp["name"])
        c_ids.append(camp["id"])
    return c_names, c_ids

class Creator: 
    def __init__(self, campaign_name = "", campaign_id = 0, email_ids = [],
                 creator_name = "", creator_phone = "", creator_sms = "", creator_domain = "", 
                 pref_country = "", pref_size = "", pref_industry = "",
                 plan = 0, week = "", month = "", creation = ""):
        # Campaign variables
        self.campaign_name = campaign_name.lower()
        self.campaign_id = campaign_id
        self.email_ids = email_ids
        # Creator variables
        self.creator_name = creator_name
        if creator_sms.replace(" ", "").lower() == "whatsapp":
            creator_phone = "whatsapp:"+creator_phone
        self.creator_phone = creator_phone
        self.creator_sms = creator_sms.replace(" ", "").lower()
        self.creator_domain = creator_domain.lower()
        # Preference variables
        self.pref_country = pref_country
        self.pref_size = pref_size
        self.pref_industry = pref_industry
        # Time variables
        if plan == 0:
            plan = 5
        self.plan = int(plan)
        self.week = week
        self.month = month
        self.creation = creation

def main():
    logger.info("Starting main loop")
    logger.info("Getting all creators from the google spreadsheet")

    # Get all creators from gSpread
    creator_list = add_creator_to_obj()
    if creator_list == None: 
        return None

    # Getting domain list and email dict from smartleads
    domain_list, email_dict = get_email_domains()
    if domain_list == None:
        return None
    
    # Check if there is any email account with the same domain name
    try:
    
        for i, creator in enumerate(creator_list):
                logger.info(f"Checking creator: {creator.creator_domain}")
                if creator.creator_domain in domain_list:
                    # Email account with the domain exists, Adding emails to Creator obj
                    logger.info("Emails in Gspread found on Smartlead, adding to Creator")
                    creator.email_ids = email_dict[creator.creator_domain]
                else:
                    # No email accounts with the creator domain which is in the Spreadsheet
                    logger.error(f"Email in Gspread not found on Smartlead for creator: {creator.creator_domain}")
                    creator_list.pop(i)
                    error(f"Email in Gspread not found on Smartlead for creator: {creator.creator_domain}")
                    continue
    except Exception as e:
        tb_str = traceback.format_exc()
        logger.critical(f"Actual error in the code during evaluation of domain lists, no changes have been made to smartleads: \n Error: {e} \n Traceback: {tb_str}")
        error(f"Actual error in the code during evaluation of domain lists, no changes have been made to smartleads: \n Error: {e} \n Traceback: {tb_str}")
        return None
    
    for i, creator in enumerate(creator_list):
        logger.info(f"Main script running for creator: {creator.creator_name}, {creator.creator_domain}")
        if creator.campaign_id != 0:
            # DAILY - WEEKLY - MONTHLY CHECKS
            # TODO run testing on these parts

            # Campaign for creator already exists, adding variables
            logger.info(f"Campaign already exists for {creator.creator_domain, creator.campaign_id}, running checks...")
            try:
                # TODO add a check to see if the amount of leads in the campaign is equal to the plan.

                # Convert time to a datetime object
                today = datetime.now()
                week = datetime.strptime(creator.week, '%Y-%m-%d')
                month = datetime.strptime(creator.month, '%Y-%m-%d')

                # Calculate the datetime for one week from now
                one_week_later = week + timedelta(weeks=1)
                one_month_later = month + relativedelta(months=1)

                # Check if one week has passed since the given time
                if today >= one_week_later:
                    # One week or more has passed 
                    logger.info("One week has passed, running check for email/day rampup")
                    # Check email/day count.
                    email_list = all_email_from_campaign(creator.campaign_id)
                    for email in email_list:
                        if email["daily_sent_count"] < 35:
                            logger.info(f"Increasing emails/day limit: { email.daily_sent_count + 5}")
                            # increase emails/day with 5
                            update_email(email["id"], rampup = 5)
                
                    # increase week in gSpread by 1
                    increase_week(i, one_week_later)
                else:
                    # Less than a week has passed
                    logger.info("Less than a week, doing nothing...")

                # Check if one month has passed since given time
                if today >= one_month_later:
                    # One month has passed
                    logger.info("One month has passed, running checks for leads")
                    # Check how many months from creation the campaign is:
                    diff_in_months = relativedelta(today, creator.creation).months
                    # Check amount of leads 
                    leads_list = get_all_leads(creator.campaign_id)
                    logger.info(f"Checking if dif in months ({diff_in_months}) times creator.plan ({creator.plan}) is larger than the amount of leads in the campaign if it is then we increase the amount of leads")
                    if len(leads_list) < diff_in_months * creator.plan:
                        # Add leads if necessary 
                        logger.info(f"Adding leads to campaign")
                        add_leads(campaign_id=creator.campaign_id, creator=creator, max=creator.plan)
                    # increase month in gSpread with 1
                    increase_month(i, one_month_later)
                else:
                    # Less than one month has passed since time
                    logger.info("Less than a month, doing nothing...")
            except Exception as e:
                tb_str = traceback.format_exc()
                logger.critical(f"Error while running daily/monthly script for creator: {creator.creator_domain} \n Error: {e} \n Traceback: {tb_str}")
                error(f"Error while running daily/monthly script for creator: {creator.creator_domain} \n Error: {e} \n Traceback: {tb_str}")
                continue
        else:
            # THIS IS THE INITIALISATION PROCESS
            # Campaign for creator does not exists, creating campaign
            try:
                logger.info(f"Running initailization protocol for creator {creator.creator_domain}: \n Campaign does not exists for {creator.creator_domain}, Creating...")
                camp_id, camp_date = create_campaign(creator.creator_domain)

                creator.campaign_name = creator.creator_domain
                creator.campaign_id = camp_id
                creator.creation = camp_date

                # TODO, Remove creator from leadlist in outgoing campaign

                # Adding emails
                add_email(creator.campaign_id, creator.email_ids)
        
                for email_id in creator.email_ids:
                    # Enable warmup on all emails
                    enable_warmup(email_id)
                    # Update email settings
                    update_email(email_id)

                # Add leads 
                # TODO Redo add leads function to create and upload 80 leads at a time until we reach the plan
                '''
                res = add_leads(creator.campaign_id, creator, creator.plan)
                if type(res) == int:
                    logger.error(f"Not enough leads added trying once more! Leads added last time: {res}")
                    add_leads(creator.campaign_id, creator, creator.plan)
                '''
                if creator.plan > 80:
                    # After free trail
                    x = m.floor(creator.plan / 80)
                    y = creator.plan - x*80

                    for i in range(0, x):
                        logger.info(f"Adding {80*i+1} leads to campaign")
                        res = add_leads(creator.campaign_id, creator, 80)
                        if type(res) == int:

                            add_leads(creator.campaign_id, creator, 80-res)
                    logger.info(f"Adding {y} leads to the campaign")
                    res = add_leads(creator.campaign_id, creator, y)
                    if type(res) == int:
                        add_leads(creator.campaign_id, creator, y-res)

                    if x*80 + y != creator.plan:
                        logger.error(f"Didn't upload enough leads uploaded {x*80 + y}, creator plan: {creator.plan}")

                else:
                    # free trail:
                    add_leads(creator.campaign_id, creator, creator.plan)


                # Add sequence
                create_sequence(creator.campaign_id)

                # Update campaign settings
                set_campaign_settings(creator.campaign_id)

                # Set campaign schedule
                set_campaign_schedule(creator.campaign_id)

                # Launch campaign
                #launch_campaign(creator.campaign_id)

                # Add variables to gSpread
                dt = datetime.fromisoformat(creator.creation.replace('Z', '+00:00')) # convert to datetime object
                time = dt.strftime('%Y-%m-%d') # format as year-month-day
                add_data_to_gspread(i, creator.campaign_id, time)

                # Send confirmation of setup message 
                send_confirmation(creator)

            except Exception as e:
                tb_str = traceback.format_exc()
                logger.critical(f"Error happened during the intialisation protocol, CHANGES TO {creator.creator_domain} CAN HAVE BEEN MADE. Error: {e}  \n Traceback: {tb_str}")
                error(f"Error happened during the intialisation protocol, CHANGES TO {creator.creator_domain} CAN HAVE BEEN MADE. Error: {e} \n Traceback: {tb_str}")
                continue

    # Sending out analytics to all creators
    logger.info("Sending out analytics")
    for creator in creator_list:
        # Get analytics from smartleads
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        stats = get_analytics(creator.campaign_id, yesterday, today)
        if stats != None:
            if int(stats["sent_count"]) > 0:
                main(creator.creator_name, stats["sent_count"], stats["open_count"], stats["reply_count"], creator.creator_phone, creator.creator_sms)
            else:
                logger.error("Skipping creator due to no emails sent during timeframe")
        else:
            logger.critical(f"Not sending analytics due to errors getting analytics {creator.campaign_id}, {creator.creator_name}, {creator.creator_phone}")
            error(f"Not sending analytics due to errors getting analytics {creator.campaign_id}, {creator.creator_name}, {creator.creator_phone}")
            return None
        
    # Upload logs 
    # TODO check why it is inappropriate (fix the sharing of log files)
    now = datetime.now()
    date_string = now.strftime("%d-%m-%Y")
    file_path = f"/home/ubuntu/app/main/logs/{date_string}.txt"

    res = upload_file_to_folder(file_path, folder_name="Logs")
    logger.info(f"Response from uploading file: {res}")
    # If this is not sent then some critical error happened during the execution of main functions
    return "ok"

if __name__ == "__main__":
    res = main()
    if res == None:
        # Something broke in the main loop
        logger.critical(f"Something broke in the main loop, exited and sleeping for 24h")
        error(f"Something broke in the main loop, exited and sleeping for 24h")
        exit()
    exit()

    