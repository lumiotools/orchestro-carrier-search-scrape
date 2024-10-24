import pandas as pd


def extractSheet2Data():
    df = pd.read_excel("data/sheet2.xlsx", sheet_name="Sheet1")
    urls = []
    print()
    for data in df["Links"]:
        urls.append(data.split("\xa0-\xa0")[1])
    return urls
