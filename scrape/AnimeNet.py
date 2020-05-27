# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 22:05:46 2019

@author: chest
"""

from scrapy.selector import Selector
from utils import *
import requests
import re

class animeSearch:
    def __init__(self):
        self.base = "https://myanimelist.net/anime/"
        self.r = requests
        self.s = Selector
        self.xpath1 = ""
        self.xpath2 = ""
        
    def createUrl(self, id):
        '''
        Create url based on id
        id: can be either Integer or String
        '''
        url = self.base + str(id)      
        req = self.r.get(url)
        req_content = req.content
        return req_content
        
    def convertSel(self, req_content):
        '''
        Initiate request call to get url and process html with Selector
        id: can be either Integer or String
        '''
        sel = self.s(text = req_content)
        return sel
    
    def determineXPath(self, sel):
        '''
        As the pages have different style, this function adjust search option
        '''
        h1 = str(sel.xpath("//div[@class='js-scrollfix-bottom']/h2[1]/text()").extract())
        b1 = 2
        b2 = 3
        if "Alternative" in h1:
            base_xpath = f"//div[@class='js-scrollfix-bottom']/h2[{b1}]/following-sibling::div"
            base_xpath2 = f"//div[@class='js-scrollfix-bottom']/h2[{b2}]/following-sibling::div"
        else:
            b1 = b1-1
            b2 = b2-1
            base_xpath = f"//div[@class='js-scrollfix-bottom']/h2[{b1}]/following-sibling::div"
            base_xpath2 = f"//div[@class='js-scrollfix-bottom']/h2[{b2}]/following-sibling::div"
        self.xpath1 = base_xpath
        self.xpath2 = base_xpath2
        return self

    @staticmethod
    def checkError(sel):
        '''
        To determine if there is an empty page which will have error404
        sel: Selector Object
        '''
        check = str(sel.xpath("//div[@class='error404']/@title").extract())
        if check  == "[]":
            return True
        else:
            return False
    
    @staticmethod
    def scrape_img(sel):
        '''
        We will extract the image url
        Minor text cleaning is done here
        '''
        img_url = str(sel.xpath("//div[@class='js-scrollfix-bottom']/div[@style='text-align: center;']//img/@src").extract())
        img_url = img_url[img_url.find("https://"):img_url.find("']")]
        return img_url
    
    @staticmethod
    def scrape_synopsis(sel):
        synopsis = str(sel.xpath("//div[@id='content']/table//td/span[@itemprop='description']/text()").extract())
        return synopsis
    
    @staticmethod
    def scrape_info(self, sel):
        '''
        We will extract the following information:
            (type, status, genre, studio, duration, rating, episodes)
        output will be in the form of dictionary 
        Minor text cleaning (removal of \n done)
        '''
        base_xpath = self.xpath1 
        base_xpath2 = self.xpath2
        length = len(sel.xpath(base_xpath))
        for div in range(1,length+1):
            span_list = sel.xpath(f'{base_xpath}[{div}]/span/text()').extract()
            if len(span_list) !=0:
                span = span_list[0]
                if span == "Type:":
                    showType = sel.xpath(f'{base_xpath}[{div}]//text()').extract()
                    showType = checklist(showType, -1)
                    showType = removeNew(showType)
                    continue    
                if span == "Episodes:":
                    episodes = sel.xpath(f'{base_xpath}[{div}]//text()').extract()            
                    episodes = checklist(episodes, -1)
                    episodes = removeNew(episodes)
                    continue    
                if span == "Status:":
                    status = sel.xpath(f'{base_xpath}[{div}]//text()').extract()
                    status = checklist(status, -1)
                    status = removeNew(status)
                    continue
                if span == "Producers:":
                    producer = sel.xpath(f'{base_xpath}[{div}]/a/text()').extract()
                    producer = flatlist(producer)
                    producer = re.sub(r'\s+', ' ', producer)
                    continue
                if span == "Studios:":
                    studio = sel.xpath(f'{base_xpath}[{div}]/a/text()').extract()
                    studio = flatlist(studio)
                    studio = re.sub(r'\s+', ' ', studio)
                    continue
                if span == "Source:":
                    source = sel.xpath(f'{base_xpath}[{div}]//text()').extract()
                    source = checklist(source, -1)
                    source = removeNew(source)
                    continue
                if span == "Genres:":
                    genre = sel.xpath(f'{base_xpath}[{div}]/a/text()').extract()
                    genre = flatlist(genre)
                    continue
                if span == "Duration:":
                    duration = sel.xpath(f'{base_xpath}[{div}]//text()').extract()
                    duration = checklist(duration, -1)
                    duration = removeNew(duration)
                    continue
                if span == "Rating:":
                    rating = sel.xpath(f'{base_xpath}[{div}]//text()').extract()
                    rating = checklist(rating, -1)
                    rating = removeNew(rating)
                    continue
                if span == "Score:":
                    score = checklist(sel.xpath(f'{base_xpath2}[1]//text()').extract(),3)
                    if score != "N/A":
                        score = float(score)
                    else:
                        score = None
                if span == "Members:":
                    member = removeNew(checklist(sel.xpath(f'{base_xpath2}[4]//text()').extract(),2))
                    member = convertNumber(member)
                    continue
                if span == "Favorites:":
                    fav = removeNew(checklist(sel.xpath(f'{base_xpath2}[5]//text()').extract(),2))
                    fav = convertNumber(fav)
        info = {"Type":showType, "Episode":episodes, "Status":status,
                  "Studio":studio, "Source":source, "Producer":producer,
                  "Genre":genre, "Duration":duration, "Rating":rating,
                  "Score":score, "Member":member, "Fav":fav}
        return info


# sample code to test
#ans = animeSearch()
#url = ans.createUrl(5114) #anime id in url
#sel = ans.convertSel(url) # get selector object
#path = ans.determineXPath(sel) # determine url path
#print(ans.scrape_info(path, sel))




