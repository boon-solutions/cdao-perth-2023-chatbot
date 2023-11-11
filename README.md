![Boon Solutions](https://www.boon.com.au/wp-content/uploads/2022/09/favicon.png)


# Boon Solutions Tooled Chatbot
Welcome to the home of our Tooled Chatbot. Powered by ChatGPT-4 and written in under 350 lines of code, Boon Solutions originally developed this app for [CDAO Perth 2023](https://cdao-perth.coriniumintelligence.com/) to showcase data privacy and the risks of LLMs when not properly managed.

## The Blog: Gen AI – Privacy, Security, and Explainability
In our data-driven reality, the boundaries that protect our personal privacy, ensure the security of our information, and clarify the decisions made by AI are not just conveniences—they are absolute necessities.
[Read more](https://www.boon.com.au/3vv5)

## The App

### Libraries
- **[Streamlit](https://streamlit.io/):** Library used to develop the app's user interface (along with some custom CSS).
- **[LangChain](https://github.com/langchain-ai/langchain):** Libraries used to develop the LLM agents thate make up the chatbot.  

### The structure
The general structure of the bot is a conversational LLM agent which is equipped with two sub-agents as tools: 
- **SQL Agent**: Used to construct and run SQL queries to any accessible databases.  
&emsp;Example prompt: *'What was the highest guess?'*
- **PGVector Agent**: Used to retrieve embedded context data from a vector database.  
&emsp;Example prompt: *'What is Boon Solutions?'*

All of these agents utilize ChatGPT-4 via [OpenAI](https://openai.com/)'s API and are developed using libraries from LangChain.

The conversational agent is also provided with memory capabilities, allowing it to retain information throughout user interactions and more efficiently retrieve prior details.

![Chatbot Structure Diagram](https://github.com/boon-solutions/cdao-perth-2023-chatbot/blob/main/images/cdao-flow.png)

The final product is a conversational chatbot that can retain details of previous messages, access information from the internet, query relevant databases, and find provided contextual information. 

### Tuning
Tweaking the tool descriptions and system messages was the primary method for tuning the chatbot's responses. This required testing across a range of questions, some of which are featured in the *'I'm feeling lucky'* button provided in the app. Testing was not only necessary to ensure the assigned tools were functioning properly but also to ensure they were being called correctly as part of the larger chatbot functionality.

![Chatbot UI Image](https://github.com/boon-solutions/cdao-perth-2023-chatbot/blob/main/images/chatbot.png)


## CDAO Perth 2023
Boasting 40+ speakers and 200+ attendees, CDAO Perth was hosted across 2 days at the Perth Convention & Exhibition Centre. Organised by [Corinium](https://www.coriniumintelligence.com/), the event brought together data experts from a range of industries to share their experience on the analytics and business intelligence landscape.

A key focus of this event was the ever growing space of artificial intelligence, including its potential use cases and associated risks. With a number of speakers expressing caution around integrating AI into business practices, Boon Solutions sought to demonstrate the power of LLMs when properly managed and designed.


## Lego Guessing Competition
The first component to Boon Solutions' demonstration was hosting a simple competition across the event's two day span where participants were tasked with guessing the number of lego pieces in a jar. Competitors were required to submit some basic, identifiable information such as name, phone number and email address in order to register their guess in the competition.

![Competition Form](https://github.com/boon-solutions/cdao-perth-2023-chatbot/blob/main/images/competition-demo.png)


## Qlik Replicate
The second stage of the demonstration is the replication and redaction of the sensitive, identifiable information collected from participants. This was achieved behind the scenes via [Qlik Replicate](https://www.qlik.com/us/lp/ppc/replicate/brand?utm_team=DIG&utm_subtype=cpc_brand&ppc_id=CTmtjVLE&kw=qlik%20replicate&utm_content=sCTmtjVLE_pcrid_81363933082488_pmt_e_pkw_qlik%20replicate_pdv_c_mslid__pgrid_1301821990031846_ptaid_kwd-81364004814404:loc-9&utm_source=bing&utm_medium=cpc&utm_campaign=Qlik_Australia_Bing_Brand_DI_Brand_EN&utm_term=qlik%20replicate&_bt=81363933082488&_bm=e&msclkid=f46dc60bc60a1aeb6947a34b996fb832), a product which redacts data in-transit between a source and target database.

The end result of this process was a usable dataset which contained no identifiable information from any of the entrants.

![Qlik Replicate UI](https://github.com/boon-solutions/cdao-perth-2023-chatbot/blob/main/images/qlik-replicate-demo.png)

If you are interested in testing Qlik Replicate on some sample data you can sign up for a trial [here](https://sites.ziftsolutions.com/qlik.ziftsolutions.com/8a9983d4842f2a95018431471c0a4d57),
or feel free to [contact us](https://github.com/boon-solutions/cdao-perth-2023-chatbot#contact-us) for a trial based off of your own data.


## Exposing Data
To complete the demonstration, the redacted dataset was exposed to our chatbot via its SQL tool. Attendees were able to view trends, aggregates and individual records of the competition via our analytics dashboard displayed at the booth, or via asking the chatbot whenever they saw fit.

Due to the chatbot operating using the ChatGPT-4 API, any information submitted to it via tools or user prompts is inherently provided to OpenAI. Had we not taken the measures to redact the dataset, all of the identifiable information of participants would have been sent to the cloud and potentially stored without their knowledge.

![Redacted Data Image](https://github.com/boon-solutions/cdao-perth-2023-chatbot/blob/main/images/redacted-data.png)

Another key point of this project is the importance of data governance when involving artificial intelligence. While ChatGPT-4 does have some self-imposed limitations on data handling, older versions such as ChatGPT-3.5 will execute hazardous SQL queries when prompted. Building in proper data security measures specifically for AI *'users'* is necessary to avoid catastrophic events such as a &ensp;```DROP TABLE table_name;```&ensp; event.

![Update Guess Image](https://github.com/boon-solutions/cdao-perth-2023-chatbot/blob/main/images/update-guess.png)


## Installation
Our chatbot code is available on GitHub: [boon-solutions/cdao-perth-2023-chatbot](https://github.com/boon-solutions/cdao-perth-2023-chatbot) 

Clone the repository:
```
$ git clone https://github.com/boon-solutions/cdao-perth-2023-chatbot
```

The chatbot is designed to run on multiple Kubernetes pods.


## Project status
While this code will be used in ongoing development and there may be future releases, for the time being this repository will remain as a static proof of concept. 

## Contact us
Email: [info@boon.com.au](mailto:info@boon.com.au)  
Website: [https://www.boon.com.au/](https://www.boon.com.au/)
