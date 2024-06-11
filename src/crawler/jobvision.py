# soelz4 - jobvision
# Library
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import requests
import pandas as pd
import time
import os

# init selenium firefox webdriver
options = webdriver.FirefoxOptions()
options.add_argument("-headless")
driver = webdriver.Firefox(
    service=FirefoxService(GeckoDriverManager().install()), options=options
)


# main function - crawler
def jobvision():

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
    base_url = "https://jobvision.ir"

    for page_num in range(1, 1000):
        # get the entire website content
        driver.get(f"https://jobvision.ir/jobs?page={page_num}&sort=0")
        html = driver.page_source
        time.sleep(2)
        print(f"page {page_num}")

        finish = False

        # bs4
        soup = BeautifulSoup(html, "html.parser")
        jobs = soup.find_all("job-card")

        # Date - Source - Title - Link - Employer - Location - Tags - Description
        for j in jobs:
            # Date
            date = j.find("span", class_="d-flex align-items-center").text.strip()
            if date != "امروز":
                finish = True
                break
            dates.append(date)
            # Source
            sources.append("jobvision")
            # Title
            title = (
                j.find(
                    "div",
                    class_="job-card-title w-100 font-weight-bolder text-black px-0 pl-4 line-height-24",
                )
                .text.strip()
                .replace("\u200c", " ")
            )
            titles.append(title)
            # Link
            # demo_link = j.find("a", id_ = "el-539961")["href"]
            demo_link = j.a["href"]
            link = f"{base_url}{demo_link}"
            links.append(link)
            # Employer
            employer = j.find(
                "a", class_="text-black line-height-24 pointer-events-none"
            ).text.strip()
            employers.append(employer)
            # Location
            location = j.find(
                "span", class_="text-secondary ng-star-inserted"
            ).text.strip()
            locations.append(location)
            # Tag
            tags.append(None)
            # Description
            inside_jobs = BeautifulSoup(requests.get(link).content, "html.parser")
            description = inside_jobs.find("div", class_="col px-0 mr-2")
            if description:
                description = description.text.replace("\xa0", "").strip()
            else:
                description = None
            descriptions.append(description)

        if finish:
            break

    # main list
    info = [titles, descriptions, employers, links, tags, sources, dates, locations]

    # dataframe
    df = pd.DataFrame(info)
    df = df.transpose()
    df.columns = header
    return df


"""
# call the function
df = jobvision()
# create csv directory for csv files
os.makedirs("../../csv", exist_ok=True)
# create csv file
df.to_csv("../../csv/jobvision.csv", index=False)
"""
