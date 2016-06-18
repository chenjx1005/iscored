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
import json
from datetime import datetime
from time import sleep
from random import random

from bs4 import BeautifulSoup


def my_get(url, headers):
    r = requests.get(url, headers=headers, proxies=proxies, timeout=5)

headers = {
       'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'accept-encoding':'gzip, deflate, sdch',
       'accept-language':'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
       'upgrade-insecure-requests':1,
#       'cookie': 'visid_incap_774904=LCtv2wUZQVypnnLhb/U/WqrBQlcAAAAAQUIPAAAAAACXiuWhXGMYozNA8X5lteMW; incap_ses_207_774904=q17xAa1g8Rdr/Akh12rfAoHGS1cAAAAA2epvjBJwOoyBpKAIQi3V3Q==; incap_ses_266_774904=P1YMDpBrOTrDuZUu1gWxA6XGS1cAAAAA0cWw7pt8SChYDXBxsZmLaw==; incap_ses_407_774904=wPSGf5ajuGj0qY5s4fSlBaLVS1cAAAAA2kYwwVnYmq6l2mGBXDwJag==; _ga=GA1.2.362616800.1464021566; _gat=1; crtg_rta=',
#       'if-modified-since': 'Mon, 30 May 2016 02:31:25 GMT',
       'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.108 Safari/537.36',
    }
    
def test_proxy(ip, port):
    proxies = {
        'http': 'http://%s:%s'%(ip, port),
        'https': 'http://%s:%s'%(ip, port),
    }
    url = 'https://www.whoscored.com/'
    r = requests.get(url, headers=headers, proxies=proxies)
    if r.status_code != 200:
        print "this proxy is unavilabel"
        return 
    if r.text.find("robots") == -1:
        print "caught as robot"
        return
    print "OK!"
    
def test_ok():
    url = 'https://www.whoscored.com/'
    r = requests.get(url, headers=headers)
    if r.text.find("robots") == -1:
        return True
    return False

def wait(delay=5, variation=1):
    m, x, c = variation, random(), delay - variation / 2
    sleep(m * x + c)

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


def tournaments():
    '''
        all_tournaments: [{type: int, id: int, flg: str, name: str, tournaments: list}]
        tournaments: {id: int, url: str, name: str}
    '''
    url = 'https://www.whoscored.com/'
    
    r = requests.get(url, headers=headers)
    rtext = r.text
    #get all tournaments
    if not os.path.isfile("all_tounaments.pkl"):
        region_text = find_between(rtext, "allRegions = ", ";")
        regions = demjson.decode(region_text)
        pickle.dump(regions, open("all_tounaments.pkl", 'w'))
        return regions
    else:
        return pickle.load(open("all_tounaments.pkl"))
        
def popular_tournaments():
    '''
        popular_tournaments: [href: str, href: str, ...]
    '''
    url = 'https://www.whoscored.com/'
    
    r = requests.get(url, headers=headers)
    rtext = r.text
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
        
def seasons(href):  
    '''
        seasons: [season: list, season: list, ....]
        season: (id: int, start_year: int, end_year: int)
    '''
    #get tournament page    
    url = 'https://www.whoscored.com' + href
    r = requests.get(url, headers=headers)
    text = r.text
    #extract seasons
    #pattern = re.compile(r'Seasons&#47;(\d+)">(\d+)&#47;(\d+)')
    pattern = re.compile(r'Seasons&#47;(\d+)">(\d+)(&#47;\d+)?</option>')
    ss = pattern.findall(text)
    for i in range(len(ss)):
        se = list(ss[i])
        if not se[-1]:
            se[-1] = se[-2]
        else:
            se[-1] = se[-1][5:]
        ss[i] = map(int, se)
    return ss
    
def stages(href, season):
    '''
        stages: [stage_id: int, ...]
    '''
    #get seasons page
    url = 'https://www.whoscored.com' + href[:href.rfind('/')] + '/Seasons/%s'%season
    r = requests.get(url, headers=headers)
    text = r.text
    #extract stage
    #if multi stages exist such as USA major league
    pattern = re.compile(r'Stages&#47;(\d+)')
    ss = pattern.findall(text)
    if ss:
        return map(int, ss)
    #only sigle stage
    else: 
        pattern = re.compile(r'/Stages/(\d+)')
        ss = pattern.findall(text)
        if ss:
            return [int(ss[0]), ]
        else:
            print url, "failed!"
            print text

def teams(href, season):
    '''
        teams: [(team_id : str, team_name: str), (team_id, team_name), ...]
    '''
    #get seasons page
    url = 'https://www.whoscored.com' + href[:href.rfind('/')] + '/Seasons/%s'%season
    r = requests.get(url, headers=headers)
    text = r.text
    
    #extract teams
    s = find_between(text, "DataStore.prime('streaks',", "] );")
    pattern = re.compile(r"\[\d+,(\d+),'([A-Za-z0-9< >]+)'")
    return pattern.findall(s)
    
def fixtures(href, season, stage):
    '''
        matches: [{match_id: int, start_time: datetime, home_id: int, home_name: str,
                  away_id: int, away_name: str, score: str}, ...]
    '''
    #get seasons page
    url = 'https://www.whoscored.com' + href[:href.rfind('/')] + \
            "/Seasons/%s/Stages/%s/Fixtures"%(season, stage)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print "status_code error!", r.status_code, url
        return False
    model_last_mode = re.findall("'Model-Last-Mode': '([^']+)'", r.text)[0]
    h = headers.copy()
    h['Model-Last-Mode'] = model_last_mode
    h['Referer'] = r.url
    h['X-Requested-With'] = 'XMLHttpRequest'
    h['accept'] = 'text/plain, */*; q=0.01'
    #extract fixtures page
    dates = re.findall("'Month', ([^ ]+), min, max", r.text)
    matches = []
    if dates:
        dates = re.sub(r'(\d+)(?=:)', r'"\1"', dates[0])
        d = json.loads(dates)

        if len(d) == 0:
            print url, "no matches"
            wait()
            return []

        months = {format(d): format(d+1, '02') for d in range(0, 12)}
        params = {'isAggregate': 'false'}
        for y in d:
            for m in d[y]:
                params['d'] = '{0}{1}'.format(y, months[m])
                wait()

                page = 'https://www.whoscored.com/tournamentsfeed/{0}/Fixtures/'.format(stage)
                r = requests.get(page, params=params, headers=h, allow_redirects=False)
                
                if r.status_code != 200:
                    print page, "status code error"
                    break
                print params['d'], "extracted."
                matchData = re.sub(r',(?=,)', r',null', r.text)
                data = json.loads(matchData.replace("'", '"'))
                
                for row in data:
                    match = {'match_id': int(row[0]), 'start_date': row[2],
                             'start_time': row[3],
                             'home_id': int(row[4]), 'home_name': row[5],
                             'away_id': int(row[7]), 'away_name': row[8],
                             'score': row[10]
                             }
                    match['start_date'] = datetime.strptime(match['start_date'], '%A, %b %d %Y')
                    match['start_time'] = datetime.strptime(match['start_time'], '%H:%M')
                    match['start_time'] = datetime.combine(match['start_date'].date(), match['start_time'].time())
                    matches.append(match)                        
    else:
        matchData = re.findall("calendarParameter\), ([^;]*)\);", r.text)
        if not matchData:
            print r.text
            print url, "no matchData"
        matchData = re.sub(r',(?=,)', r',null', matchData[0])
        data = json.loads(matchData.replace("'", '"') if matchData else '{}')

        for row in data:
            match = {'match_id': int(row[0]), 'start_date': row[2],
                     'start_time': row[3],
                     'home_id': int(row[4]), 'home_name': row[5],
                     'away_id': int(row[7]), 'away_name': row[8],
                     'score': row[10]
                     }
            match['start_date'] = datetime.strptime(match['start_date'], '%A, %b %d %Y')
            match['start_time'] = datetime.strptime(match['start_time'], '%H:%M')
            match['start_time'] = datetime.combine(match['start_date'].date(), match['start_time'].time())
            matches.append(match)  
    wait()
    return matches
    
def have_stat(href, season):
    #get seasons page
    wait()
    url = 'https://www.whoscored.com' + href[:href.rfind('/')] + \
            "/Seasons/%s"%season
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print url, "status code error", r.status_code
        raise ValueError
    soup = BeautifulSoup(r.text)
    sub = soup.select('div #sub-navigation')
    if not sub:
        print r.text
        print url, "does not have sub-navigation"
    ul = sub[0]
    a_player_stat = ul.select("a")[-1]
    inactive = a_player_stat.attrs['class'][0]
    if inactive == 'inactive':
        return False
    return True
    

def player_stat_permatch(match, home, away):
    '''
        stats: [stat_home: list, stat_away: list]
        stat_home: [player: dict, ...]
        player: {'shot': float, 'save': float, ..., 'playerId': int, 'name': str...}
    '''
    #print match
    #get match page
    url = 'https://www.whoscored.com/Matches/%s/LiveStatistics' % match
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print "match has not started", url
        return []
    model_last_mode_list = re.findall("'Model-Last-Mode': '([^']+)'", r.text)
    if not model_last_mode_list:
        print r.text
        print "I can't find model last_mode_list."
        print "we will wait 50 seconds and retry once."
        wait(100)
        r = requests.get(url, headers=headers)
        model_last_mode_list = re.findall("'Model-Last-Mode': '([^']+)'", r.text)
        if not model_last_mode_list:
            print "retry fail"
            raise requests.exceptions.ConnectionError
    model_last_mode = model_last_mode_list[0]
    h = headers.copy()
    h['Model-Last-Mode'] = model_last_mode
    h['Referer'] = r.url
    h['X-Requested-With'] = 'XMLHttpRequest'
    h['accept'] = 'application/json, text/javascript, */*; q=0.01'
    #get home and away stat
    wait()
    page = 'https://www.whoscored.com/StatisticsFeed/1/GetMatchCentrePlayerStatistics'
    stats = []
    for team in [home, away]:
        params = {'category':'summary',
                  'subcategory':'all',
                  'statsAccumulationType':0,
                  'teamIds':team,
                  'matchId':match,
                  'isCurrent':'true',}
        try:
            stat = requests.get(page, params=params, headers=h, allow_redirects=False)
        except requests.exceptions.ConnectionError as e:
            print e
            print "we will wait 50 seconds and retry once."
            wait(100)
            stat = requests.get(page, params=params, headers=h, allow_redirects=False)
        stat_json = json.loads(stat.text)
        stats.append(stat_json['playerTableStats'])
    return stats

if __name__ == "__main__":
    ip = "213.129.34.28"
    port = 3128
    proxies = {
        'http': 'http://%s:%s'%(ip, port),
        'https': 'http://%s:%s'%(ip, port),
    }
    url = 'https://www.whoscored.com/'
    r = requests.get(url, headers=headers, proxies=proxies, timeout=5)
    text = r.text
    if r.status_code != 200:
        print "this proxy is unavilabel"

    if r.text.find("robots") == -1 and r.text.find("ROBOTS") == -1:
        print "OK"
    else:
        print "caught as a robot"
    