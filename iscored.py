# -*- coding: utf-8 -*-
"""
Created on Thu May 26 04:25:55 2016

@author: cc
"""

import json
from datetime import datetime

from sql import db, Region, Tournament, PopTournament, Season, Stage, Team,\
                Match, PlayerStatPerMatch, Player
from extract import wait, test_ok, tournaments, popular_tournaments, seasons, stages,\
                    fixtures, have_stat, player_stat_permatch

def build_regions_tournaments():
    regions = tournaments()
    for r in regions:
        region = Region(region_id=r['id'], type=r['type'],
                        flg=r['flg'], name=r['name'])
        region.save()
        for t in r['tournaments']:
            Tournament.create(region=region, tournament_id=t['id'],
                              name=t['name'], url=t['url'])
                              
def build_popular_tournaments():
    pops_url = popular_tournaments()
    for u in pops_url:
        tournamet = Tournament.get(Tournament.url==u)
        PopTournament.create(tournament=tournamet)
        
def build_season():
    for p in PopTournament.select():
        u = p.tournament.url
        ss = seasons(u)
        wait()
        print p.tournament.name, "extracted."
        for s in ss:
            Season.create(tournament=p.tournament, season_id=s[0],
                          begin_year=s[1], end_year=s[2])
                          
def build_stage():
    for se in Season.select():
        if se.stages:
            print se.tournament.name, se.begin_year,\
                "-", se.end_year, "already in db."
            continue
        se_id = se.season_id
        tournament_url = se.tournament.url
        sts = stages(tournament_url, se_id)
        wait()
        print se.tournament.name, se.begin_year, "-", se.end_year, "extracted."
        for st in sts:
            if not Stage.select().where(Stage.stage_id==st):
                Stage.create(season=se, stage_id=st)
            else:
                print se.tournament.name, se.begin_year,\
                "-", se.end_year, st, "already in db."
    
def build_match_team():
    for p in PopTournament:
        u = p.tournament.url
        for se in p.tournament.seasons:
            for st in se.stages:
                matches = fixtures(u, se.season_id, st.stage_id)
                print p.tournament.name, se.begin_year, "-", se.end_year, \
                        " ", st.stage_id, "extracted."
                for ma in matches:
                    #save home and away team
                    home_sql = Team.select().where(Team.team_id==ma['home_id'])
                    if home_sql:
                        home = home_sql.get()
                    else:
                        home = Team(team_id=ma['home_id'], name=ma['home_name'])
                        home.save()
                    away_sql = Team.select().where(Team.team_id==ma['away_id'])
                    if away_sql:
                        away = away_sql.get()
                    else:
                        away = Team(team_id=ma['away_id'], name=ma['away_name'])
                        away.save()
                    #save match
                    Match.create(stage=st, match_id=ma['match_id'], time=ma['start_time'],
                                home=home, away=away, score=ma['score'])
                                
def build_player_stat_permatch():
    cont = False
    pops = [t.tournament for t in PopTournament]
    pops.sort(key=lambda x: x.tournament_id)
    #pass premirer league and bundesiliga, la liga, series A
    for p in pops[4:]:
        u = p.url
        #if not use list(), program will crash. 
        #see https://github.com/coleifer/peewee/issues/81
        for se in list(p.seasons.order_by(Season.season_id.desc())):
            tournament_name = p.name + "%s - %s"%(se.begin_year,se.end_year)
            if not have_stat(u, se.season_id):
                print tournament_name, "does not have statistics."
                continue
            print tournament_name, "has statistics, begin to extract."
            for st in list(se.stages.order_by(Stage.stage_id.desc())):
                for ma in list(st.matches.order_by(Match.match_id.desc())):
                    #continue from last break match
                    if ma.match_id == 830370:
                        cont = True
                    if not cont:
                        continue
                    stat = player_stat_permatch(ma.match_id, ma.home.team_id,
                                                ma.away.team_id)
                    for team_stat in stat:
                        for p_stat in team_stat:
                            player_id = p_stat['playerId']
                            name = p_stat['name']
                            stat_info = json.dumps(p_stat)
                            player, created = Player.get_or_create(player_id=player_id,
                                                                   name=name)
                            ps, created = PlayerStatPerMatch.get_or_create(match=ma,
                                                      player=player,
                                                      defaults={'stat_info': stat_info})
                    print datetime.now(), tournament_name, ma.match_id, "extracted."
                    

if __name__ == "__main__":
    db.connect()
    if test_ok():
            build_player_stat_permatch()
        
    else:
        print "caught as a robot!"
    db.close()