from contextlib import closing
from selenium.webdriver import Chrome, PhantomJS
from selenium.webdriver.support.ui import WebDriverWait
import bs4 as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

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
	
    chrome_options = webdriver.ChromeOptions()
    #prefs = {"profile.managed_default_content_settings.images": 2}
    prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'stylesheet':2,
                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
                            'durable_storage': 2}}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless")
    #chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    driver = Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

    #driver = PhantomJS()

    search_string=""
    b=""
    for x in query:
        if x == ' ':
            search_string=search_string+b+"%20"
            b=""
        else:
            b=b+x
    search_string=search_string+b
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

