# Necessary libraries to be imported
from bs4 import BeautifulSoup as bs
import requests
from typing import TypedDict
import json
import jmespath
# from .autoProgress import printProgressBar
# import gspread
# import pandas as pd
from datetime import datetime
import time
from result import Ok, Err, Result

''' create Beautiful Soup XML parsing content, focus on three things:

- The __NEXT_DATA__ content
- The number of pages
- The next page button

'''

# This store the urls we would like to retrieve
PROS_URL : str = 'https://prosple.com/search-jobs?study_fields=502&keywords=Graduate+Program&defaults_applied=1&locations=9692&opportunity_types=1&sort=newest_opportunities|desc'

# #### ***1.1 Prosple Scraping***

# Let's create an output type by using typing

class Job(TypedDict):
    prosple_id: str
    title: str
    name: str
    logo: str
    app_source: str
    type: str
    location: str
    shr_desc: str
    # lng_desc: str
    # str_date: str
    opn_date: str
    cls_date: str
    vac: str
    minsal: int
    maxsal: int
    condsal: str
    rights: list[str]


# Let's create a function that extract all of the previous information into a list of Job objects
def extract_job(job_data) -> Job:
    return Job({
        'prosple_id': jmespath.search('id', job_data),
        'title': jmespath.search('title', job_data),
        'name': jmespath.search('parentEmployer.title', job_data),
        'logo': jmespath.search('parentEmployer.logo.thumbnail.url', job_data),
        'app_source': jmespath.search('applyByUrl', job_data),
        'type': jmespath.search('opportunityTypes[0].label',job_data),
        'location': jmespath.search('locationDescription', job_data),
        'shr_desc': jmespath.search('overview.summary', job_data),
        # 'str_date': datetime.fromisoformat(
        #     jmespath.search('startDate.exactDate', job_data)
        # ).strftime("%Y-%m-%d") 
        # or 
        # jmespath.search('startDate.category.label', job_data),
        'opn_date': None if jmespath.search('applicationsOpenDate', job_data) is None \
        else datetime.fromisoformat(
            jmespath.search('applicationsOpenDate', job_data)
        ).strftime("%Y-%m-%d"),
        'cls_date': None if jmespath.search('applicationsCloseDate', job_data) is None \
        else datetime.fromisoformat(
            jmespath.search('applicationsCloseDate', job_data)
        ).strftime("%Y-%m-%d"),
        'vac': str(jmespath.search('minNumberVacancies', job_data))
        + ' - ' + str(jmespath.search('maxNumberVacancies', job_data)),
        'minsal': 0 if jmespath.search('minSalary', job_data) is None   \
        else jmespath.search('minSalary', job_data), 
        'maxsal': 0 if jmespath.search('maxSalary', job_data) is None   \
        else jmespath.search('maxSalary', job_data),
        'condsal': jmespath.search('additionalBenefits', job_data),
        'rights': jmespath.search('workingRights[0].children[*].label', job_data),
        # 'lng_desc': bs(jmespath.search('overview.fullText', job_data), 'html.parser').text,
    })

# another function to extract all job in a page
def extract_page(url: str) -> list[:]:
    response = requests.get(url)
    # let's soup'd and extract the data (in the json format)
    data_souped = bs(response.text, 'html.parser')              \
                    .select('script#__NEXT_DATA__')[0].text
    # and jsonified the data into a Python Dict
    data_jsoned = jmespath.search(
        'props.pageProps.initialResult.opportunities',
        json.loads(data_souped)
    ) 
    
    output_list = []
    for job in data_jsoned:
        output_list.append(extract_job(job))

    return output_list

def get_page_count(prosple_url: str=PROS_URL) -> int:
    return int(jmespath.search(
        'props.pageProps.initialResult.resultCount',
        json.loads(bs(requests
    .get(prosple_url)
    .text,'html.parser').select('script#__NEXT_DATA__')[0].text))) // 20

def extract_prosple(prosple_url : str=PROS_URL) -> None:
    # Get the PAGE COUNT to see how many values are there
    page_count = get_page_count(prosple_url = prosple_url)

    final_list = []
    # for page in range(0,page_count*20+20,20):
    for page in range(0,1):
        final_list += extract_page(prosple_url + '&start=' + str(page))
        
        # current_prog = 50*page//(page_count*20)
        # printProgressBar(current_prog,
        #                 50,
        #                 prefix='Prosple Scraping Progress:',
        #                 suffix='complete',
        #                 length=50
        #                 )
    print(final_list) #for debug
    # time.sleep(0.15)
    # outputdf = pd.DataFrame(final_list)

    # outputdf['rights'] = outputdf['rights'].apply(lambda x: ','.join([i for i in x]))
    # outputdf['opn_date'] = outputdf['opn_date'].apply(lambda x: x[0:10] if x else None)
    # outputdf['cls_date'] = outputdf['cls_date'].apply(lambda x: x[0:10] if x else None)
    # outputdf['str_date'] = outputdf['str_date'].apply(lambda x: (x[0:10] if len(x) > 4 else x) if x else None)
    # outputdf['minsal'] = outputdf['minsal'].apply(lambda x: x if x else 0)
    # outputdf['maxsal'] = outputdf['maxsal'].apply(lambda x: x if x else 0)

    return final_list


if __name__ == "__main__":
    # output_df = extract_prosple(prosple_url=PROS_URL)
    print(get_page_count())