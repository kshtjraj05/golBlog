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
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True
    #button = WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnmore"]')))
    page_source = driver.page_source
    soup = bs.BeautifulSoup(page_source)
    #print(soup)
    link=[]
    post_title=[]
    for div in soup.find_all('div', class_="postArticle-content"):
        print('Hey')
        for url in div.find_all('a'):
            link.append(url.get('href'))
        for title in div.find_all('div', class_='section-content'):
            post_title.append(title.get_text())
    print(link)
    print(post_title)
lst=['kubernetes']
scrape_medium(lst)
'''while(True):
        try:
            button.click()
            button = WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnmore"]')))		
            page_source = driver.page_source
        except:
            break
    driver.quit()
    df = pd.DataFrame(columns=['Recipe_Name','Recipe_Link','Main_Ingredient','Cuisine','Course','Veg'])

    soup = bs.BeautifulSoup(page_source)
    base_url="https://www.sanjeevkapoor.com"
    count=0
    for div in soup.find_all('div', class_ = 'col-md-6 images-blog1'):
        print(count)
        count+=1
        for url in div.find_all('a'):
            obj=Row()
            real_url=urljoin(base_url,url.get('href'))
            print(real_url)
            dic=obj.prepare_row(real_url)
            dic['Recipe_Link']=base_url+real_url
            x=dic['Recipe_Link'].rindex('/')
            x+=1
            y=dic['Recipe_Link'].rindex('.')
            dic['Recipe_Name']=dic['Recipe_Link'][x:y]
            df=df.append(dic, ignore_index=True)
    df.to_excel('SK_scraped.xlsx')
'''
