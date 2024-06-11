# soelz4 - jobinja
# Library
import requests
import pandas as pd
import time
import os
from bs4 import BeautifulSoup


def jobinja_crawler():
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

    base_url = "https://jobinja.ir/"
    for page_number in range(1, 444):
        url = f"https://jobinja.ir/jobs/latest-job-post-%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85%DB%8C-%D8%AC%D8%AF%DB%8C%D8%AF?&page={page_number}&preferred_before=1718087762&sort_by=published_at_desc"
        time.sleep(2)
        page = requests.get(url, timeout=5)
        print(f"page {page_number} - {page}")  # 200 - 299

        finish = False

        # bs4
        soup = BeautifulSoup(page.content, "html.parser")
        jobs = soup.find_all(
            "div", class_="o-listView__itemWrap c-jobListView__itemWrap u-clearFix"
        )

        # Date - Source - Title - Link - Employer - Location - Tags - Description
        for job in jobs:
            # Source
            sources.append("jobinja")
            # Date
            date = (
                job.find("span", class_="c-jobListView__passedDays")
                .text.replace("(", "")
                .replace(")", "")
                .strip()
            )
            if date != "امروز":
                finish = True
                break
            dates.append(date)
            # Title
            title = job.find("a", class_="c-jobListView__titleLink").text.strip()
            titles.append(title)
            # Employer and Location
            temp = []
            li = job.find_all("li", class_="c-jobListView__metaItem")
            for i in li:
                for j in i.find_all("span"):
                    temp.append(j.text.strip())
            employer = temp[0]
            employers.append(employer)
            location = temp[1]
            locations.append(location)
            # Link
            link = job.find("a", class_="c-jobListView__titleLink").get("href")
            links.append(link)
            # Inside Jobs
            inside_jobs = BeautifulSoup(requests.get(link).content, "html.parser")
            # Description
            if inside_jobs.find("div", class_="o-box__text s-jobDesc c-pr40p"):
                description = inside_jobs.find(
                    "div", class_="o-box__text s-jobDesc c-pr40p"
                ).text.strip()
                descriptions.append(description)
            elif inside_jobs.find("div", class_="o-box__text s-jobDesc u-ltr c-pl40p"):
                description = inside_jobs.find(
                    "div", class_="o-box__text s-jobDesc u-ltr c-pl40p"
                ).text.strip()
                descriptions.append(description)
            else:
                descriptions.append(None)
            # Tag
            _tags = []
            for tag in inside_jobs.find_all("span", class_="black"):
                _tags.append(
                    tag.text.replace("\n", "")
                    .replace("  ", "")
                    .replace("مهم نیست", "")
                    .replace("u200c", "")
                    .strip()
                )
            tags.append(_tags)
        if finish:
            break

    # main list
    info = [titles, descriptions, employers, links, tags, sources, dates, locations]

    # DataFrame
    df = pd.DataFrame(info)
    df = df.transpose()
    df.columns = header
    return df


'''
# Call the Function
df = jobinja_crawler()
# Create CSV Directory for CSV Files
os.makedirs("../../csv", exist_ok=True)
# Create CSV File
df.to_csv("../../csv/jobinja.csv", index=False)
'''
