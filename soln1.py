import pandas as pd
import datetime as dt
import random
from time import sleep

def generateData( start=dt.datetime(2020, 6, 21), end=dt.datetime(2020, 9, 28) ):

    """This generates random data for clients issues

    Args:
        start (datetime): Start Time for issues to be generated from
        end (datetime): Time till which data is to be generated

    Returns:
        DataFrame: returns the required data in pandas dataframe 
    """

    AbandonResolve = [0, 1]
    df = pd.DataFrame({"StartTime": [], "R/A": [],"AnswerTime": [], "ResolvedTime": [], "AbandonTime": []})

    print("Generating issue data...")

    while(start <= end):
        minutes = random.randrange(5)
        ans = start + dt.timedelta(minutes=minutes)
        c = random.choice(AbandonResolve)
        if(c):
            abd = 0
            minutes = random.randrange(10)
            res = ans + dt.timedelta(minutes=minutes)
            a,b,c,d,e = start, c, ans, res, abd
            start = res
        else:
            res = 0
            minutes = random.randrange(10)
            abd = ans + dt.timedelta(minutes=minutes)
            a,b,c,d,e = start, c, ans, res, abd
            start = abd
        
        df = df.append({"StartTime": a, "R/A": b, "AnswerTime": c,"ResolvedTime": d, "AbandonTime": e}, ignore_index=True)

    print("Data generated!")
    
    return df


def dataprocessing(df):

    """Process the generated DataFrame to find hourly wait time for clients

    Args:
        df (Dataframe): contains client's issues data

    Returns:
        DataFrame: waiting times for clients
    """
    print("Finding Wait time...")

    wait = []
    df["StartTime"] = pd.to_datetime(df["StartTime"])
    df["AnswerTime"] = pd.to_datetime(df["AnswerTime"])
    df["ResolvedTime"] = pd.to_datetime(df["ResolvedTime"],errors='coerce')
    df["AbandonTime"] = pd.to_datetime(df["AbandonTime"],errors='coerce')

    for a, b, c, d, e in df.values:
        if(b):
            wait.append((d-a).seconds)
        else:
            wait.append((e-a).seconds)

    df["Wait"] = wait
    hourlywait = (df.groupby(((df["StartTime"].dt.dayofweek)*24) + (df["StartTime"].dt.hour + 1))["Wait"].mean()
                  .rename_axis('HourOfWeek')
                  .reset_index())

    return hourlywait


def predictWait(issue, df):
    """predict waiting time for clients

    Args:
        issue (datetime): timestamp when the issue was registered  
        df (DataFrame): waiting times for clients

    Returns:
        Countdowns the waiting time
    """
    seconds = df[df["HourOfWeek"] ==((issue.weekday())*24) + (issue.hour + 1)]["Wait"]
    for i in range(int(seconds), 0, -1):
        print("An agent will respond in " +  str(dt.timedelta(seconds=i)), end = '\r')
        sleep(1)
    return "An agent responded in " +  str(dt.timedelta(seconds=int(seconds)))


def NewIssue():
    """Predicts Waiting Time and countdown it
    """
    try:
        df = pd.read_csv("issues.csv", index_col=0)
    except :
        print("Data not found!!")
        df = generateData(s, e)
        df.to_csv("issues.csv")
    wait = dataprocessing(df)
    while(True):
        try:
            day, month , year = map(int,input("Date [DD/MM/YYYY] : ").split("/"))
            hour,min = map(int,input("Time [HH:MM] : ").split(":"))
            issue = dt.datetime(year,month,day,hour) 
        except :
            print("Datetime Format not valid!!")
            continue   
        print(predictWait(issue, wait))
        choice = input("do you want to continue? (y/n):")
        if choice.lower()[0]=="n":
            break