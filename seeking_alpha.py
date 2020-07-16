import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
import datetime as dt
import requests
import numpy as np


url = "https://seekingalpha.com/symbol/AAPL"

fx_options = webdriver.FirefoxOptions()
fx_options.set_headless()

browser = webdriver.Firefox(options=fx_options)

browser.get(url)

# Selenium script to scroll to the bottom, wait 3 seconds for the next batch of data to load, then continue scrolling.  It will continue to do this until the page stops loading new data.
lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
count = 0
while count < 1:
    lastCount = lenOfPage
    time.sleep(3)
    lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    count += 1

# Now that the page is fully scrolled, grab the source code.
c = browser.page_source

browser.quit()

soup = BeautifulSoup(c, "html.parser")

news = soup.find_all("div", {"class", "symbol_article"})

l = []

#the analysis has a date, the news has a value like time = "1588196120"

for item in news:
    d = {}
    article_title = item.find('a', href=True)
    href = 'http://www.seekingalpha.com' + item.find_all('a', href=True)[0]['href']
    try:
        type = "article"
        date = item.find('span', {"class", "date"})
        if date is not None:
            d['date'] = date.text
        if date is None:
            type = 'news'
            date = item.attrs['time']
            d['date'] = date
    except:
        type = 'news'
        date = None
        d['date'] = date
    d['type'] = type
    d["article_title"] = article_title.next
    d['href'] = href
    l.append(d)

title_date_df = pd.DataFrame(l)

#now we have to manipulate the dates to something usable




def date_for_titles_posted_today(date_str):
    """
    when pulling from seeking things posted today have form 'Today, 9:45 AM', this function takes that string and converts
    it to a datetime
    Args:
        date_str: a date string of form eg 'Today, 9:45 AM'

    Returns:

    """
    today_at_midnight = dt.datetime.combine(dt.date.today(), dt.datetime.min.time())

    hour = int(date_str.split(',')[1].split(':')[0].replace(" ", ""))
    minute_string = date_str.split(',')[1].split(':')[1][:2]
    #need to deal with case where minute = 01
    if minute_string[0] == '0':
        minute = int(minute_string[-1])
    else:
        minute = int(minute_string)
    date_posted = today_at_midnight + dt.timedelta(hours = hour, minutes = minute)
    return date_posted


def date_for_analysis_titles_before_today(link):
    browser = webdriver.Firefox(options=fx_options)
    browser.get(link)
    soup = BeautifulSoup(browser.page_source)
    time_string = soup.find_all('time')[0].text
    split_time_string = time_string.split(" ")
    month = split_time_string[0].replace(".", "").replace(" ", "")
    day = split_time_string[1].replace(",","").replace(" ", "")
    year = split_time_string[2].replace(",","").replace(" ", "")
    am_pm = split_time_string[5]
    hour = split_time_string[4].split(":")[0] # need to convert in and out of int to make 24 hour reformatting easier
    if len(hour) == 1:
        hour = "0" + hour
    minute = split_time_string[4].split(":")[1]
    reformatted_date_string = month + ', ' + day + ', ' + year + ', ' + hour + ', ' + am_pm + ', '+ minute
    date = dt.datetime.strptime(month + ", " + day + ', ' + year + ', ' + hour + ', ' + am_pm + ', '+ minute, '%b, %d, %Y, %I, %p, %M')
    return date


def date_from_unix_timestamp(date_str):
    """
    articles are returned with unix timestamp,
    Args:
        date_str: unix timestamp string

    Returns: datetime

    """
    unix_date = int(date_str)
    date = dt.datetime.utcfromtimestamp(unix_date).strftime('%Y-%m-%d %H:%M:%S')
    return date


dl = title_date_df.iloc[:, 0]

date_for_titles_posted_today(dl[0])

l=[]
for i in range(len(dl)):
    temp = str(dl[i])
    if temp.split()[0] == 'Yesterday,':
        l.append(date_for_titles_posted_today(temp))
    if len(temp) == 10:
        l.append(date_from_unix_timestamp(temp))



