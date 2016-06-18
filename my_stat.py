# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 15:54:40 2016

@author: cc
"""

import json
import pandas as pd
from datetime import datetime

from sql import db, Region, Tournament, PopTournament, Season, Stage, Team,\
                Match, PlayerStatPerMatch, Player
from player_stat_config import INVAL_STAT

def parse_incidents(incs):
    incident = {"Pass": 0,
                "Goal": 0,
                "OwnGoal": 0,
                "ShotOnPost": 0,
                "Yellow": 0,
                "Red": 0,
                "SecondYellow": 0,
                "Tackle": 0,
                "Error": 0,
                "Save": 0,
                "SavedShot": 0,
                "PenaltyFaced": 0,
                }
    for inc in incs:
        inc_type = inc['type']['displayName']
        #some basic type
        if inc_type in ("Pass", "ShotOnPost", "Tackle", "Error", "Save",
                        "SavedShot", "PenaltyFaced"):
            incident[inc_type] += 1
        #goal and own goal
        elif inc_type == "Goal":
            if not inc['isOwnGoal']:
                incident["Goal"] += 1
            else:
                incident["OwnGoal"] += 1
        #yellow and red card
        elif inc_type == "Card":
            card_type = inc['cardType']
            if card_type:
                incident[card_type['displayName']] += 1
        #subsititution
        elif inc_type in ("SubstitutionOff", "SubstitutionOn"):
            pass
        #some other types are all assit in whoscored
        elif inc_type in ("MissedShots", 'BallTouch', 'BlockedPass', 'Clearance',
                          'CornerAwarded', 'Interception', 'Punch', 'TakeOn',
                          'Turnover', 'Aerial', 'Foul'):
            incident['Pass'] += 1
        else:
            raise KeyError("new incident type %s" % inc_type)
    return incident

def parse_stat(info):
    info_dict = json.loads(info)
    for key in INVAL_STAT:
        del info_dict[key]
    #'incidents' must be dealed with seprately
    incident = parse_incidents(info_dict['incidents'])
    del info_dict['incidents']
    info_dict.update(incident)
    return info_dict

def db2csv(filename):
    #write keys into csv
    with open(filename, 'w') as w:
        s = PlayerStatPerMatch.get()
        info = s.stat_info
        info_dict = parse_stat(info)
        info_dict['match_id'] = 0
        info_dict['player_id'] = 0
        keys = ",".join(info_dict.keys()) + '\n'
        w.write(keys)
        #write values
        for i, s in enumerate(PlayerStatPerMatch):
            match_id = s.match.match_id
            player_id = s.player.player_id
            info = s.stat_info
            info_dict = parse_stat(info)
            info_dict['match_id'] = match_id
            info_dict['player_id'] = player_id
            value_str = map(str, info_dict.values())
            values = ",".join(value_str) + '\n'
            w.write(values)

if __name__ == "__main__":
    df = pd.read_csv("PlayerStatPerMatch.csv")