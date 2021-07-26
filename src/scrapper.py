import pathlib
import time
import math
import sys
import json
import numpy as np
import os
import urllib.request

from tqdm import tqdm
from datetime import datetime
from datetime import date
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException


class ScrapePlateNumber :
    # Initialization Function
    def __init__(self):
        self.data                   = {}
        self.scraping_script_path   = pathlib.Path(__file__).parent.absolute()
        self.driver                 = str(self.scraping_script_path) + "/driver/chromedriver"
        self.path                   = str(self.scraping_script_path) + "/img/"
        self.site_url               = "https://www.google.com"
        self.tqdm                   = tqdm
        self.page_scroll_sleep      = 2
        print(self.driver)

    # Method for Initializing Chrome Web Driver and its Configuration
    def initBrowser(self):
        print("Scraping Module : Initiating Scraping for : " + str(self.site_url))

        # Initializing Chrome Web Driver and its Configuration
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("window-size=1920x1080")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")

        try:
            self.browser = webdriver.Chrome(
                self.driver,
                options=chrome_options,
            )
        except WebDriverException as webDriverException:
            print(
                "Issue with Chrome Driver. Incorrect version of Chrome Driver or Chrome Driver Not Present"
            )
            sys.exit(
                "Issue with Chrome Driver. Incorrect version of Chrome Driver or Chrome Driver Not Present"
            )

        print("Scraping Module : Opening Chrome To Start Data Scraping")
        self.wait = WebDriverWait(self.browser, 20)

    # Method to load URL
    def loadURL(self):
        # Opening Kijiji Website
        print("Opening webiste : " + self.site_url)
        try :
            self.browser.get(self.site_url)
            print("gotten url")
            self.browser.maximize_window()
            return True
        except:
            return False

    # Method to set search Location parameters
    def searchKeyword(self, kwy):

        try:
            address_box = self.wait.until(EC.element_to_be_clickable((By.NAME, 'q')))
            address_box.send_keys(kwy)
            time.sleep(5)
            address_box.send_keys(Keys.ENTER)
            time.sleep(10)
            print("Keyword")
        except TimeoutException as timeoutException:
            address_box.send_keys(' ')
            address_box.send_keys(Keys.ENTER)
            print("Issue while Entering and Searching the Location. Check your Internet Connection and Re-run the Program")
            raise Exception("Issue while Entering and Searching the Location. Check your Internet Connection and Re-run the Program")
            sys.exit()

    # Method to set Language to English
    def changeToImages(self):
        # Update Language to English
        try:
            links = self.browser.find_elements_by_tag_name("a")
            for link in links:
                print( link.text)
                if link.get_attribute('data-hveid') == "CAEQAw":
                    url = link.get_attribute('href')
                    break
            self.browser.get(url)
            time.sleep(20)
            print("gotten url " + url)
            print("Images section Loaded")
        except TimeoutException as timeoutException:
            print("Issue while updating tO Images. Check your Internet Connection and Re-run the Program")
            sys.exit("Issue while updating tO Images. Check your Internet Connection and Re-run the Program")

    # Method to check for null
    def null_count(self, list_):
        '''This will take in a list of scraped image links, counts/returns 
        how many null values the list contains. 
        '''
        null_count = 0
        
        for element in list_:
            if element == None:
                null_count += 1
                
        return null_count

    # Method to scrol down to load all images
    def scrollDown (self, data_name, max_imgs=200):
        # print(self.tqdm)
        # if self.tqdm._instances :
        #     self.tqdm._instances.clear()
        folder_name = data_name + "/"
        file_name = data_name.replace(" ", "-")
        
        # Get scroll height
        last_height = self.browser.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(self.page_scroll_sleep)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.browser.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break
            #break #insert press load more
                try:
                    element = self.browser.find_elements_by_class_name('mye4qd') #r0zKGf
                    element[0].click()
                    time.sleep(10)
                    print("Bottom page reached")
                except:
                    print("Issue while scrolling down Images. Check your Internet Connection and Re-run the Program")
                    sys.exit("Issue while scrolling down Images. Check your Internet Connection and Re-run the Program")
            last_height = new_height
        
        # gets link list of images
        if max_imgs == 0:
            links = self.getImagesLink(200)    
        else:   
            links = self.getImagesLink(max_imgs)        
        sleeps = [1,0.5,1.5,0.7]
        
        # urllib save images into folder and renames using data_name string
        for i,link in enumerate(tqdm(links)):
            
            img_name =  self.path + folder_name + file_name +  "-"
            name = img_name+f'{i}.jpeg'

            urllib.request.urlretrieve(link, name)
            time.sleep(np.random.choice(sleeps))
            
        self.browser.quit()

    # Method to set Language to English
    def getImagesLink(self, max_imgs):
        # Update Language to English
        try:
            image_links = self.browser.find_elements_by_class_name('rg_i.Q4LuWd')
            src_links = [image_links[i].get_attribute('src') for i in range(len(image_links))]
            data_src_links = [image_links[i].get_attribute('data-src') for i in range(len(image_links))]
            nc_src = self.null_count(src_links)
            nc_datasrc = self.null_count(data_src_links)
    
            if nc_src > nc_datasrc:
                for i,element in enumerate(data_src_links):
                    if element == None:
                        data_src_links[i] = src_links[i]
                
                if len(data_src_links) > max_imgs:
                    return data_src_links[:max_imgs]
                else:
                    return data_src_links
        
            else: 
                for i,element in enumerate(src_links):
                    if element == None:
                        src_links[i] = data_src_links[i]
                
                if len(src_links) > max_imgs:
                    return src_links[:max_imgs]
                else:
                    return src_links

        except TimeoutException as timeoutException:
            print("Issue while updating tO Images. Check your Internet Connection and Re-run the Program")
            sys.exit("Issue while updating tO Images. Check your Internet Connection and Re-run the Program")

    # Method to control the flow of execution of scrapping
    def startScrapper(self, keyword, max_imgs):
        keyword.strip()
        self.initBrowser()
        url_is_loaded = self.loadURL()

        if url_is_loaded:
            folder_name = keyword + "/"
            os.mkdir(self.path + folder_name)
            self.searchKeyword(keyword)
            time.sleep(5)
            self.changeToImages()
            time.sleep(5)
            self.scrollDown(keyword, max_imgs)
            # self.getImagesLink()
        else:
            sys.exit()



if __name__ == '__main__':
    get_keyword = input("Enter Keyword : ")
    max_imgs = input("Enter No. of Images Required : ")
    if max_imgs == "" or max_imgs.isnumeric() == False:
        max_imgs = 0

    pl = ScrapePlateNumber()
    pl.startScrapper(get_keyword, int(max_imgs))