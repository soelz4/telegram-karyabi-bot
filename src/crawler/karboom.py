# soelz4 - karboom
# Library
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import os


# main function - crawler
def karboom_crawler():

    # Lists
    sources = []
    links = []
    dates = []
    tags = []
    titles = []
    locations = []
    descriptions = []
    employers = []
    header = [
        "title",
        "description",
        "employer",
        "link",
        "tags",
        "source",
        "date",
        "locations",
    ]

    # base url
    base_url = "https://karboom.io/"

    for page_num in range(1, 1000):
        url = f"https://karboom.io/jobs?page={page_num}"
        time.sleep(2)
        page = requests.get(url, timeout=5)
        print(f"page {page_num} - {page}")  # 200 - 299

        finish = False

        # bs4
        soup = BeautifulSoup(page.content, "html.parser")
        jobs = soup.find_all("div", class_="box-intro js-job-item flex-col-between")

        # Date - Source - Title - Link - Employer - Location - Tags - Description
        for j in jobs:
            # Date
            if j.find("p", class_="immediate-employment color-danger"):
                date = j.find(
                    "p", class_="immediate-employment color-danger"
                ).text.strip()
            elif j.find("p", class_="date sm-text-size kb-text-gray-light m-0"):
                date = j.find(
                    "p", class_="date sm-text-size kb-text-gray-light m-0"
                ).text.strip()
            if date != "امروز" and date != "Today" and date != "فوری":
                finish = True
                break
            dates.append(date)
            # Source
            sources.append("karboom")
            # Title
            title = (
                j.find("h3", class_="sm-title-size ellipsis-text width-100 m-0")
                .text.replace("\u200c", " ")
                .strip()
            )
            titles.append(title)
            # Link
            link = j.a["href"]
            links.append(link)
            # Employer
            employer = j.find(
                "span", class_="company-name ellipsis-text m-0"
            ).text.strip()
            employers.append(employer)
            # Location
            location = j.find("span", class_="pull-right").text.strip()
            locations.append(location)
            # Tags
            tags.append(None)
            # Inside Jobs
            inside_jobs = BeautifulSoup(requests.get(link).content, "html.parser")
            # Description
            temp = inside_jobs.find_all("div", class_="job-detail-box")
            for v in temp:
                s = v.text.strip()
                if "شرح شغل / وظایف" in s or "Job Description / Tasks" in s:
                    description = v.find("div", class_="md-text-size")
                    description = (
                        description.text.replace("\xa0", "").replace("؛", "").strip()
                    )
                    break
                else:
                    description = None
            descriptions.append(description)
        if finish:
            break

    # main list
    info = [titles, descriptions, employers, links, tags, sources, dates, locations]

    # DataFrame
    df = pd.DataFrame(info)
    df = df.transpose()
    df.columns = header
    return df


"""
# call the function
df = karboom_crawler()
# create csv directory for csv files
os.makedirs("../../csv", exist_ok=True)
# create csv file
df.to_csv("../../csv/karboom.csv", index=False)
"""
