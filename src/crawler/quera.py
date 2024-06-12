# soelz4 - quera
# Library
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import os


# main function - crawler
def quera_crawler():

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
    base_url = "https://quera.org/"

    for page_num in range(1, 4):
        url = f"https://quera.org/magnet/jobs?page={page_num}"

        time.sleep(2)

        page = requests.get(url, timeout=5)
        print(f"page {page_num} - {page}")  # 200 - 299

        finish = False

        # bs4
        soup = BeautifulSoup(page.content, "html.parser")
        jobs = soup.find_all("div", class_="chakra-stack css-1b6q6b6")

        # Date - Source - Title - Link - Employer - Location - Tags - Description
        for job in jobs:
            # Date
            # Date
            if (
                job.find("div", class_="chakra-stack css-nm8t2j").find("span").text
                != "یک روز پیش"
            ):
                date = (
                    job.find("div", class_="chakra-stack css-nm8t2j")
                    .find("span")
                    .get("title")
                )
            else:
                finish = True
                break
            dates.append(date)
            # Source
            sources.append("karboom")
            # Title
            title = job.find("a", class_="chakra-link css-spn4bz").text.strip()
            titles.append(title)
            # Employer
            employer = job.find("p", class_="chakra-text css-1m52y4d").text.strip()
            employers.append(employer)
            # Link
            link = "https://quera.org/" + job.find(
                "a", class_="chakra-link css-4a6x12"
            ).get("href")
            links.append(link)
            # Location
            if job.find("div", class_="chakra-stack css-5ngv18"):
                location = (
                    job.find("div", class_="chakra-stack css-5ngv18")
                    .find("span")
                    .text.strip()
                )
                locations.append(location)
            else:
                locations.append(None)
            # Inside Job
            inside_jobs = BeautifulSoup(requests.get(link).content, "html.parser")
            # Description
            if inside_jobs.find("div", class_="css-7viiwh"):
                description = (
                    inside_jobs.find("div", class_="css-7viiwh")
                    .text.replace("\n", " ")
                    .replace("\u200c", " ")
                    .strip()
                )
                descriptions.append(description)
            else:
                descriptions.append(None)
            # Tag
            _tags = []
            main_tags = job.find_all("div", class_="chakra-stack css-1iyteef")
            side_tags = job.find_all("span", class_="css-1qy3adt")
            prime_tags = job.find_all("span", class_="css-h1qgq")

            for tag in side_tags:
                for span in tag.find_all("span"):
                    _tags.append(span.text.strip())

            for tag in prime_tags:
                for span in tag.find_all("span"):
                    _tags.append(span.text.strip())

            for tag in main_tags:
                for span in tag.find_all("span"):
                    _tags.append(span.text.replace("\u200c", " ").strip())
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


"""
# call the function
df = quera_crawler()
# create csv directory for csv files
os.makedirs("../../csv", exist_ok=True)
# create csv file
df.to_csv("../../csv/quera.csv", index=False)
"""
