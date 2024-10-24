import pandas as pd


def extractSheet2Data():
    df = pd.read_excel("data/sheet1.xlsx", sheet_name="Sheet1")
    print(df.head())
    return
