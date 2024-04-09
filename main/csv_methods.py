import csv
import random
import os
import traceback
from gpt_methods import get_cold_email, get_follow_ups
from analytics import logger
from analytics import error
from filtered import generate_csv

class leads:
    def __init__(self,
                  firstname = "", 
                  lastname = "", 
                  company = "", 
                  company_link = "", 
                  linkedin = "", 
                  email = "", 
                  website = "", 
                  position = "", 
                  location = "",
                  cold_mail_body = "",
                  follow_ups = []):
        self.firstname = firstname
        self.lastname = lastname
        self.company = company
        self.comapny_link = company_link
        self.linkedin = linkedin
        self.email = email
        self.website = website
        self.position = position
        self.location = location
        self.cold_mail_body = cold_mail_body
        self.follow_ups = follow_ups

# Open the CSV file for reading
def get_data_from_csv(filepath, creator, max_leads):
    with open(filepath, 'r', encoding='utf-8') as csvfile:
        # Create a CSV reader object¨
        try:
            reader = csv.reader(csvfile)
            
            rows = list(reader)
            row_count = len(rows)
            #check if there is enough leads in csv:
            if row_count-1 < max_leads:
                # TODO, Implement master csv logic
                logger,error(f"Not enough leads in csv, sending error for creator: {creator.creator_name}, {creator.creator_domain}")
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.critical(f"Error while getting lead data from csv file. Error: {e} \n traceback: {tb_str}")
            error(f"Error while getting lead data from csv file. Error: {e} \n traceback: {tb_str}")
            return None
            
        # Loop through each row in the CSV file
        if max_leads*8 < row_count:
            sample_max = max_leads*3    
        else:
            sample_max = row_count-1
            
        random_indicies = random.sample(range(1, row_count), sample_max) # Max tries to reach obj_list is 8 times the max leads
        object_list = list()
        used_leads = list()

        for index in random_indicies:
            row = rows[index]

            # Skip testing data
            if row[1] == "Test":
                continue
            
            elif len(object_list) < max_leads:
                # Initialize object
                logger.info(f"Generating lead obj: {len(object_list) + 1} index: {index}")
                lead_obj = leads()
                # Append the value in the desired column to the list
                try:
                    lead_obj.firstname = row[0]
                    lead_obj.lastname = row[1]
                    lead_obj.email = row[2]
                    lead_obj.company = row[3]
                    lead_obj.position = row[4]
                    # unnecessary row[5] - comp size
                    #i.linkedin = row[6]
                    lead_obj.website = row[7]
                    # unnecessary rows 8, 9, 10, 11
                    lead_obj.location = row[12]
                    # unnecessary row 13 industry
                except Exception as e:
                    logger.error(f"Error while adding data to lead obj {index}, skipping...")
                    continue
                try:
                    lead_obj.cold_mail_body = get_cold_email(lead_obj.firstname, lead_obj.position, lead_obj.company, lead_obj.website, creator)
                    lead_obj.follow_ups = get_follow_ups(lead_obj.cold_mail_body, lead_obj.firstname, creator)
                    logger.info(f"Email for {lead_obj.firstname}: \n\n Cold email: {lead_obj.cold_mail_body} \n\n Follow-ups: {lead_obj.follow_ups}")
                    if lead_obj.follow_ups == None or lead_obj.cold_mail_body == None:
                        logger.error(f"Error while generating email or followup.")
                        continue

                except Exception as e:
                    logger.error(f"Broke while generating emails for lead. skipping... {e}")
                    continue

                object_list.append(lead_obj)
                used_leads.append(index)
            else:
                logger.info(f"Added: {len(object_list)}, to lead obj, skipping the rest")
                break
    
    # Make new csv with unused rows
    new_rows = list()
    logger.info(f"Leads to be removed: {used_leads}")
    for index, row in enumerate(rows):
        if index not in used_leads:
            new_rows.append(row)
        else:
            continue
    
    write_data_to_csv(filepath, new_rows)
    del new_rows
    return object_list

def create_csv(creator):
    logger.info(f"Creating csv based on the {creator.creator_domain} preferences: {creator.pref_country}, {creator.pref_size}, {creator.pref_industry}")
    country = creator.pref_country.replace(", ", "/")
    industry = creator.pref_industry.replace(", ", "/")
    size = creator.pref_size.replace(", ", "/")    
    keywordString = f"{country},{size},{industry}"
    logger.info(keywordString)
    generate_csv(keywordString, creator)

def write_data_to_csv(filepath, rows):
    logger.info(f"Deleting old file and making new csv with new data to csv at {filepath}")
    try:
        os.remove(filepath)
    except Exception as e:
        logger.error(f"Couldn't remove old csv file, trying overwriting... {filepath}")

    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
            writer.writerow(row)
    #TODO Add a check if writing worked
