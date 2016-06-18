# -*- coding: utf-8 -*-
"""
Created on Thu May 26 01:08:30 2016

@author: cc
"""

from peewee import *

db = SqliteDatabase('whoscored.db')

class Base(Model):
    class Meta:
        database = db # This model uses the "people.db" database.

class Region(Base):
    region_id = IntegerField()
    type = IntegerField()
    flg = CharField()
    name = CharField()

class Tournament(Base):
    region = ForeignKeyField(Region, related_name='tournaments')
    tournament_id = IntegerField()
    name = CharField()
    url = CharField()
    
class PopTournament(Base):
    tournament = ForeignKeyField(Tournament, related_name='pop_tournaments')

class Season(Base):
    tournament = ForeignKeyField(Tournament, related_name='seasons')
    season_id = IntegerField()
    begin_year = IntegerField()
    end_year = IntegerField()#end year of the season
    
class Stage(Base):
    season = ForeignKeyField(Season, related_name='stages')
    stage_id = IntegerField()
    
class Team(Base):
    team_id = IntegerField()
    name = CharField()
    
class Player(Base):
    player_id = IntegerField()
    name = CharField()
    
class Match(Base):
    stage = ForeignKeyField(Stage, related_name='matches')
    match_id = IntegerField()
    time = DateTimeField()
    home = ForeignKeyField(Team, related_name='homes')
    away = ForeignKeyField(Team, related_name='aways')
    score = CharField()
    
class PlayerStatPerMatch(Base):
    match = ForeignKeyField(Match, related_name='playerstats')
    player = ForeignKeyField(Player, related_name='permatchstats')
    stat_info = CharField()

if __name__ == "__main__":       
    db.connect()
    db.create_tables([PlayerStatPerMatch])
    db.close()