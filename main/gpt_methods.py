import openai
from html_methods import main
from analytics import logger
from analytics import error

def open_key(file_path):
    with open(file_path, 'r') as file:
        key = file.read()
    return key

# INITIAL VAR
openai.api_key = open_key("/home/ubuntu/app/main/keys/key_openai.txt")
spacing_string = "<div><p></p></div>"


def get_cold_email(name, position, company, website, creator):
    text = main(website)
    if text == None:
        logger.info(f"Text list == None, {text}. Skipping generating email")
        return None
    logger.info(f"Generating cold email: {name}, {company} from: {creator.creator_name}, {creator.creator_domain}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
                {"role": "system", "content": '''
As an AI, your task is to compose a personalized cold email from a creator to the head of marketing at a target brand. 
The email should demonstrate that the UGC creator has researched the brand by including 2-3 sentences referencing their website. 
The objective is to pique the recipient's interest in hiring The UGC creator for content creation. 
Base the email on the UGC creator's cold email outreach templates, and emphasize The UGC creator's ability to create attention-grabbing content that drives viewer interest and product purchases for any brand. 
Focus on UGC creator's expertise in crafting compelling content that resonates with the target audience, rather than her own following.
                '''}, 
                {"role": "user", "content": f'''
Exclude subject line from email. Refrain from including any [Insert] boxes in the email body.

The Name of the writer/UGC creator is {creator.creator_name}.

The recipient of the email is {name} {position} at {company}.

Here is the first text from the site. {text}
                '''}
            ]
    )
    email = response['choices'][0]['message']['content'].replace("\n\n", spacing_string)
    return email

def get_follow_ups(email, name, creator):
    logger.info(f"Generating follow-ups for: {name}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.5,
        messages=[
                {"role": "system", "content": '''As an AI, your task is to compose four short personalized follow-up emails from a UGC creator to the head of marketing at a target brand. 
                These follow-up emails should be based on an initial cold email that we will provide. In each follow-up email, continue to demonstrate that the UGC creator has researched the brand by including 2-3 sentences referencing their website. 
                The objective is to maintain the recipient's interest in hiring the UGC creator for content creation. Base the follow-up emails on UGC creator cold email outreach templates, and emphasize the UGC creator's ability to create attention-grabbing content that drives viewer interest and product purchases for any brand. 
                Focus on the UGC creator's expertise in crafting compelling content that resonates with the target audience, rather than their own following.
                '''}, 
                
                {"role": "user", "content": 
'''Write four short personalized follow-up emails.

Make each email 2-3 short sentences and use different angles on each one. 
Old email:
            
Hi George,
                        
I hope this email finds you well. My name is Tiger and I am a UGC creator who specializes in creating attention-grabbing content that makes the viewer want to purchase the product being showcased. I came across The Furniture Makers' Company and I was thoroughly impressed with the work that you do to support and sustain the British furnishing industry.

As a UGC creator, I believe that I can help showcase your products in a way that will make them stand out and grab the attention of potential customers. My focus is on creating content that is engaging, informative, and visually appealing. With my skills, I can create content that not only showcases your products but also tells a story that resonates with your audience.

I would love to discuss the possibility of collaborating with you to create content that will help promote your brand and products. I am confident that my skills and experience will be a valuable asset to your team.

Thank you for considering my proposal. I look forward to hearing back from you soon.

Best regards,
Tiger

from the sender Tiger to George. Do not include a subject line for the emails. Make sure to include newlines and commonly used spacing practices. 
Make the goal of the email the follow-up to them to reply to Tiger and for George to want to work with them. The follow-ups should be concise and only include what's essential.
'''},
                
                {"role": "assistant", "content":
'''1:
Hi George,

I hope you're doing well. I wanted to follow up on the email I sent you last week. I'm still interested in the opportunity to collaborate with The Furniture Makers' Company. 
I think my skills as a UGC creator will be a great asset to your team. Let me know if you're available to chat further.

Best regards,
Tiger
2:
Hi George,

I just wanted to check in and see if you had a chance to review my previous email. I'm excited about the opportunity to work with The Furniture Makers' Company and I think my skills as a UGC creator will be a great fit. 
Let me know if you have any questions or concerns.

Best regards,
Tiger
3:
Hi George,

I hope this email finds you well. I wanted to follow up on our previous conversations regarding a possible collaboration. 
I believe that my skills as a UGC creator could greatly benefit The Furniture Makers' Company. If you're interested in moving forward, let's schedule a call to discuss further.
Best regards,
Tiger

4:
Hi George,

I wanted to touch base and see if you had any updates regarding a possible collaboration. I'm still interested in working with The Furniture Makers' Company and I believe that my skills as a UGC creator could help promote your brand and products.
Let me know if you have any questions or if there's anything else I can provide to help move things forward.

Best regards,
Tiger
'''},
                
                {"role": "user", "content": f'''Write four short personalized follow-up emails.
Make each email 2-3 short sentences and use different angles on each one.
Old email: {email}
'''}
            ]
    )
    try:
        res = response['choices'][0]['message']['content']
        a, b = res.split("1:")
        b, c = b.split("2:")
        c, d = c.split("3:")
        d, e = d.split("4:")
        b = b[1:].replace("\n\n", spacing_string)
        c = c[1:].replace("\n\n", spacing_string)
        d = d[1:].replace("\n\n", spacing_string)
        e = e[1:].replace("\n\n", spacing_string)
        arr = [b, c, d, e]
        return arr
    except Exception as e:
        logger.error(f"Failed to create follow up emails. Error: {e}")
        logger.error(f"Response to followups: {response}")
        return None