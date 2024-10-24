import pandas as pd


def extractSheet1Data():
    # Read the Excel file
    df = pd.read_excel('data/sheet1.xlsx')
    
    # Extract URLs from the second column
    df = df[321].dropna()
    urls=[]
    for data in df:
         print(data)
         urls.append(data)
    return urls

