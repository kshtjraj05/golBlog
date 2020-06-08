from contextlib import closing
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
import bs4 as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import pandas as pd
import urllib.request
#from dem4 import Row
from urllib.parse import urljoin
from selenium.webdriver.chrome.options import Options
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time

# instantiate a chrome options object so you can set the size and headless preference
#chrome_options = Options()
#hrome_options.add_argument("--headless")
#chrome_options.add_argument("--window-size=1366X768")
#chrome_options.add_argument('--disable-gpu')
def scrape_medium(query):
	
    driver = Chrome(ChromeDriverManager().install())
    search_string=""
    for x in query:
        search_string = search_string +"%20"+x
    search_string=search_string[3:]
    driver.get(f'https://medium.com/search?q={search_string}')
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    i=1
    while(match==False and i<=2):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True
        i+=1
    page_source = driver.page_source
    soup = bs.BeautifulSoup(page_source)
    user_link=[]
    username=[]
    for div in soup.find_all('div',class_='postMetaInline-authorLockup'):
        for url in div.find_all('a'):
            if url.get('data-action') == 'show-user-card' and url.get('data-action-source') != None:
                username.append(url.get_text())
                user_link.append(url.get('href'))
    dates=[]
    for date in soup.find_all('time'):
        dates.append(date.get_text())
    link=[]
    post_title=[]
    for div in soup.find_all('div', class_="postArticle-content"):
        for url in div.find_all('a'):
            link.append(url.get('href'))
        for title in div.find_all('div', class_='section-content'):
            post_title.append(title.get_text())

    i=0
    lst=[]
    dic={}
    for i in range(len(username)):
        dic['username']=username[i]
        dic['user_link']=user_link[i]
        dic['link']=link[i]
        dic['title']=post_title[i]
        dic['date']=dates[i]
        lst.append(dic)
        dic={}
    return lst

