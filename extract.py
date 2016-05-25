# -*- coding: utf-8 -*-
"""
Created on Thu May 26 01:08:30 2016

@author: cc
"""

import re
import os
import pickle
import requests
import demjson
from bs4 import BeautifulSoup

headers = {
       'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'accept-encoding':'gzip, deflate, sdch',
       'accept-language':'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
       'upgrade-insecure-requests':1,
       'cookie': 'visid_incap_774904=LCtv2wUZQVypnnLhb/U/WqrBQlcAAAAAQUIPAAAAAACXiuWhXGMYozNA8X5lteMW; incap_ses_266_774904=26CubdWKjhq+7t8Z1gWxAzAYRVcAAAAA2WEuRu0Mm+W0lwKkLl+9UQ==; incap_ses_407_774904=aBx+DK2X03vAnexX4fSlBSdBRVcAAAAARdYsU17os+WZEC9NKDD4JA==; _gat=1; _ga=GA1.2.362616800.1464021566; crtg_rta=',
       'if-modified-since': 'Wed, 25 May 2016 06:05:17 GMT',
       'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.108 Safari/537.36',
    }

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def extract_homepage(s):
    
    url = 'https://www.whoscored.com/'
    
    r = s.get(url, headers=headers)
    return r

def tournaments(rtext):
    '''
        popular_tournaments: [href: str, href: str, ...]
    '''
    #get all tournaments
    if not os.path.isfile("all_tounaments.pkl"):
        region_text = find_between(rtext, "allRegions = ", ";")
        regions = demjson.decode(region_text)
        pickle.dump(regions, open("all_tounaments.pkl", 'w'))
    
    #get popular tournaments
    if not os.path.isfile("popular_tounaments.pkl"):
        popular_href = []
        soup = BeautifulSoup(rtext)
        pop = soup.select('#popular-tournaments-list')[0]
        for li in pop.contents:
            a = li.contents[0]
            href = a.attrs['href']
            popular_href.append(href)
        pickle.dump(popular_href, open("popular_tounaments.pkl", 'w'))
        return popular_href
    else:
        return pickle.load(open("popular_tounaments.pkl"))
        
def seasons(s, href):  
    '''
        seasons: [season: str, season: str, ....]
    '''
    #get tournament page    
    url = 'https://www.whoscored.com' + href
    r = s.get(url, headers=headers)
    text = r.text
    #extract seasons
    pattern = re.compile(r'Seasons&#47;(\d+)')
    return pattern.findall(text)
    
def stages(s, href, season):
    '''
        stage_id: str
    '''
    #get seasons page
    url = 'https://www.whoscored.com' + href[:href.rfind('/')] + '/Seasons/%s'%season
    r = s.get(url, headers=headers)
    text = r.text
    #extract stage
    pattern = re.compile(r'/Stages/(\d+)')
    return pattern.findall(text)[0]

def teams(s, herf, seasons):
    '''
        teams: [(team_id : str, team_name: str), (team_id, team_name), ...]
    '''
    #get seasons page
    url = 'https://www.whoscored.com' + href[:href.rfind('/')] + '/Seasons/%s'%season
    r = s.get(url, headers=headers)
    text = r.text
    #extract teams
    s = find_between(text, "DataStore.prime('streaks',", "] );")
    pattern = re.compile(r"\[\d+,(\d+),'([A-Za-z0-9< >]+)'")
    return pattern.findall(s)
    


def fixtures(s, href, season, stage):
    #get seasons page
    url = 'https://www.whoscored.com' + href[:href.rfind('/')] + '/Seasons/%s'%season
    r = s.get(url, headers=headers)
    text = r.text
    #extract fixtures page
    soup = BeautifulSoup(text)
    sub = soup.select('#sub-navigation')[0]
    fixtures_href = sub.select("a")[1].attrs['href']
    r = s.get('https://www.whoscored.com'+fixtures_href, headers=headers)
    text = r.text
    
    

def matches_teams(s, stage, d):
    pass


    
s = requests.Session()
r = extract_homepage(s)
popular_href = tournaments(r.text)

premier = popular_href[0]
premier_season = seasons(s, premier)