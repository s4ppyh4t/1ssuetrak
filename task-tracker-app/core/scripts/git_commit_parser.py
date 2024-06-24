import json
import requests
import jmespath
# from dotenv import load_dotenv
import os
from result import Ok, Err, Result
from pathlib import Path
from itertools import groupby
import datetime

# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# load_dotenv(f"{BASE_DIR}/.env")
def get_commits( dest: str = "") -> Result[requests.Response, str]:
    
    """INTERNAL FUNCTION - look for `scrape_commits`

    Retrieve commits list based on resquest URL provided 

    Args:
        dest (_type_, optional): _description_. Defaults to "https://api.github.com/repos/s4ppyh4t/dj4e-practice/commits".

    Returns:
        requests.Response: _description_
    """
    url = str(dest)
    load : requests.Response
    try:
        load = requests.api.get(
            headers= {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {os.environ['GITHUB_SECRET_KEY']}",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            url=url)
        # return Err(f"Shit testing")
        return Ok(load)
    except Exception as e:
        return Err(f"A connection error has occured. Please check your internet connection.\nERROR: {e}")


def scrape_commits(url : str ) -> Result[dict, str]:
    """Read commit records from GitHub API endpoint "List commits".
    Return a list of commit dicts, containing commit's URL, author, committer and comment if no error is raised.

    Find out more about this GitHub API endpoint [here](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28)
    
    Parameter(s):
        `url`: the endpoint URL in the following format `https://api.github.com/repos/<OWNER>/<REPO>/commits`
    
    Returns:
        `Result[Ok(dict), Err(str)]`: The Result type from [result](https://pypi.org/project/result/). 
        Either a dictionary (interface via `Ok` class) or an error string (via `Err` class)
    """
    data_js = jmespath.search(     # Search for necessary data in Response's content payload
                    expression="[*].[html_url,commit.author.name,commit.committer.name,commit.committer.date,commit.message]",
                    data=json.loads(get_commits(dest=url).unwrap().content), 
                )                  # Load commits content from source by calling `get_commits`
    try:
        data_dict : dict = [
            {                      # Form a record (dictionary) for each recs
                "commit_url":rec[0],
                "commit_author":rec[1],
                "commit_committer":rec[2],
                "commit_datetime":datetime.datetime.fromisoformat(rec[3]).strftime("%H:%M:%S"),
                # datetime.
                "commit_date": datetime.datetime.fromisoformat(rec[3]).strftime("%Y-%m-%d"),
                "commit_comment":rec[4],
            } 
                for rec in data_js # Load commits content from source by calling `get_commits``
            ]
        
        data_dict = sorted(data_dict, key=lambda k: k["commit_date"],reverse=True)
        # for key, value in groupby(data_dict, lambda k: k["commit_date"]):
        #     print(key)
        #     print(list(value))

        return_dict = { a[0] : list(a[1]) for a in groupby(data_dict, lambda k: k["commit_date"]) }
        # for item in return_dict.items():
        #     print(item[0])
        return Ok(return_dict)
    except Exception as e:
        return Err(f"The script has encountered an error.\nMost likely, it is due to the fact that your request has returned an JSON-unparsable format\nERROR: {e}")

if __name__ == "__main__":
    # scrape_commits(url="")
    a = scrape_commits(url="https://api.github.com/repos/s4ppyh4t/dj4e-practice/commits")
    print(a)
__all__ = ["scrape_commits"]
