import requests
import json
import csv
from analytics import error
from analytics import logger

url = 'https://test.bytechserver.com/getSearchResults2'
headers = {
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': '*/*',
    'Referer': 'https://app.ugclists.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.75 Safari/537.36',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Origin': 'https://app.ugclists.com'
}
data = {
    "netnew": False,
    "sortsize": None,
    "sortcompany": None,
    "sortcontact": None,
    "userid": "nT7lm2tUJmhJ40mTcBg0OMPr81v1",
    "keywords": None,
    "companyName": None,
    "companySize": [],
    "jobTitle": None,
    "locations":[1431],
    "industries": [],
    "limit": 50000,
    "offset": 0
}
locations ={
    'United Kingdom':[1431,'uk'],
    'Canda':[1432,'cand'],
    'Australia':[1433,'aus'],
    'France':[1438,'fra'],
    'Germany':[1437,'GER'],
    'Italy':[1435,'italy'],
    'Netherlands':[1434,'nthland'],
    'Spain':[1436,'spain'],
    'United States':[1430,'us'],
    'No preference':[]
    }
industry = {
    'Apparel & fashion':[2038],
    'Computer games':[2044],
    'Consumer electronics':[2045],
    'Cosmetics':[2040],
    'Dairy':[2046],
    'Food & beverages':[2036],
    'Furniture':[2042],
    'Health, wellness & fitness':[2039],
    'Luxury goods & jewelry':[2037],
    'Software & apps':[2048],
    'Sporting goods':[2043],
    'Travel & hospitality':[2047],
    'Wine & spirits':[2041],
    'No preference':[]
}
size={
    '1-10':[{"from":1,"to":10}],
    '10-100':[{"from":10,"to":50},{"from":50,"to":100}],
    '100-1000':[{"from":100,"to":1000}],
    '1000+':[{"from":1000,"to":None}],
    'No preference':[]
}


def generator(filterKeywords, creator):
    keywordList = []
    if type(filterKeywords) == str:
        keywordList.append(filterKeywords)
    else:
        keywordList = filterKeywords

    for keyword in keywordList:
        filters = keyword.split(',')
        locationList = []
        location = filters[0].split('/')
        for j in location:
            try:
                locationList.append(locations[j][0])
            except:
                locationList = []
                break

        # For generating master CSV
        if filters[0] == "No preference" and filters[1] == "No preference" and filters[3] == "No preference":
            for _,item in locations.items():
                data['locations'] = [item]
                #print(data)
                response = requests.post(url, json=data, headers=headers)
                #print(response)
                json_response = json.loads(response.content)

                # Define the fields you want to extract from the JSON data
                fields = ['firstname', 'lastname', 'email', 'companyname', 'jobtitle', 'companysize', 'inlink', 'weblink', 'twitterlink', 'instalink', 'fblink', 'personalinlink', 'location', 'industry']

                # Open the CSV file for writing
                with open('data.csv', 'a', newline='',encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fields)

                    # Write the header row to the CSV file
                    writer.writeheader()

                    # Write each row of data to the CSV file
                    for contact in json_response['contacts']:
                        row = {field: contact.get(field, '') for field in fields}
                        writer.writerow(row)
            break
        
        try:
            companySizes = []
            company = filters[1].split('/')
            for j in company:
                companySizes = companySizes + size[j]

            industries = []
            indus = filters[2].split('/')
            for j in indus:
                industries = industries + industry[j]
            filename = []

            for j in location:
                try:
                    filename = filename + [locations[j][1]]
                except:
                    filename = []
            if len(filename) == 0:
                filename = ""
            else:
                filename = ",".join(filename)
            filename = filename + "_" + filters[1].replace('/',',') + "_" + filters[2].replace('/',',') + ".csv"
            filename = filename.replace(',','-').replace('&','_')
            data['locations'] = locationList
            data['companySize'] = companySizes
            data['industries'] = industries
        except Exception as e:
            #TODO; Make real error handling and use master csv instead as temporary fix 
            print(e)
            exit()

        response = requests.post(url, json=data, headers=headers)
        json_response = json.loads(response.content)
            # Define the fields you want to extract from the JSON data
        fields = ['firstname', 'lastname', 'email', 'companyname', 'jobtitle', 'companysize', 'inlink', 'weblink', 'twitterlink', 'instalink', 'fblink', 'personalinlink', 'location', 'industry']
        filename = "/home/ubuntu/app/main/csv/" + creator.creator_domain + ".csv"
            # Open the CSV file for writing
        with open(filename, 'w', newline='',encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)

                # Write the header row to the CSV file
            writer.writeheader()

                # Write each row of data to the CSV file
            for contact in json_response['contacts']:
                row = {field: contact.get(field, '') for field in fields}
                if filters[0].lower() != 'no preference':
                    if row['location'].lower() in filters[0].lower():
                        writer.writerow(row)
                else:
                    writer.writerow(row)
        logger.info(f"Finished creating CSV file for {creator.creator_domain} With the filename of {filename}")


def generate_csv(filterKeywords, creator):
    try:
        generator(filterKeywords, creator)
    except Exception as e:
        logger.critical(f"Error while generating custom csv for {creator.creator_domain}")
        error(f"Error while generating custom csv for {creator.creator_domain}, {e}")

if __name__ == "__main__":
    generate_csv("United States/United Kingdom,1-10/10-100,wine & spirits/travel & hospitality")