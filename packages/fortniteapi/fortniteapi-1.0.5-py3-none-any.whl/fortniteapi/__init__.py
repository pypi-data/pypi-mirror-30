# Import necessary libraries
import urllib.request
import json
import sys

class tracker:

    def __init__(self, api_key, user=None, platform=None, user_agent=None):
        self.api_key = api_key
        if user_agent != None:
            self.user_agent = user_agent
        else:
            self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
        if user != None:
            self.user = user
        if platform != None:
            self.platform = platform

    def setUser(self, user):
        self.user = user
        
    def setPlatform(self, platform):
        self.platform = platform

    def get_stats(self):
        self.url = "https://api.fortnitetracker.com/v1/profile/" + self.platform + "/" + self.user
        self.header = {"TRN-Api-Key": self.api_key, "User-Agent": self.user_agent}
        self.req = urllib.request.Request(self.url, headers=self.header)
        self.resp = urllib.request.urlopen(self.req)
        self.resp = self.resp.read()
        self.parsed = json.loads(self.resp)
        
        self.EPIC_USER = self.parsed["epicUserHandle"]
        self.FULL_PLATFORM = self.parsed["platformNameLong"]

        self.ALL_SOLO_WINS = self.parsed["stats"]["p2"]["top1"]["value"]
        self.ALL_SOLO_TOP3 = self.parsed["stats"]["p2"]["top3"]["value"]
        self.ALL_SOLO_TOP5 = self.parsed["stats"]["p2"]["top5"]["value"]
        self.ALL_SOLO_TOP6 = self.parsed["stats"]["p2"]["top6"]["value"]
        self.ALL_SOLO_TOP10 = self.parsed["stats"]["p2"]["top10"]["value"]
        self.ALL_SOLO_TOP12 = self.parsed["stats"]["p2"]["top12"]["value"]
        self.ALL_SOLO_TOP25 = self.parsed["stats"]["p2"]["top25"]["value"]
        self.ALL_SOLO_KD = self.parsed["stats"]["p2"]["kd"]["value"]
        try:
            self.ALL_SOLO_WIN_CHANCE = self.parsed["stats"]["p2"]["winRatio"]["value"] + "%"
        except:
            self.ALL_SOLO_WIN_CHANCE = "0.00%"
        self.ALL_SOLO_GAMES = self.parsed["stats"]["p2"]["matches"]["value"]
        self.ALL_SOLO_KILLS = self.parsed["stats"]["p2"]["kills"]["value"]
        self.ALL_SOLO_KPG = self.parsed["stats"]["p2"]["kpg"]["value"]
        self.ALL_SOLO_AVG_TIME_PER_GAME = self.parsed["stats"]["p2"]["avgTimePlayed"]["value"]

        self.ALL_DUO_WINS = self.parsed["stats"]["p10"]["top1"]["value"]
        self.ALL_DUO_TOP3 = self.parsed["stats"]["p10"]["top3"]["value"]
        self.ALL_DUO_TOP5 = self.parsed["stats"]["p10"]["top6"]["value"]
        self.ALL_DUO_TOP6 = self.parsed["stats"]["p10"]["top6"]["value"]
        self.ALL_DUO_TOP10 = self.parsed["stats"]["p10"]["top10"]["value"]
        self.ALL_DUO_TOP12 = self.parsed["stats"]["p10"]["top12"]["value"]
        self.ALL_DUO_TOP25 = self.parsed["stats"]["p10"]["top25"]["value"]
        self.ALL_DUO_KD = self.parsed["stats"]["p10"]["kd"]["value"]
        try:
            self.ALL_DUO_WIN_CHANCE = self.parsed["stats"]["p10"]["winRatio"]["value"] + "%"
        except:
            self.ALL_DUO_WIN_CHANCE = "0.00%"
        self.ALL_DUO_GAMES = self.parsed["stats"]["p10"]["matches"]["value"]
        self.ALL_DUO_KILLS = self.parsed["stats"]["p10"]["kills"]["value"]
        self.ALL_DUO_KPG = self.parsed["stats"]["p10"]["kpg"]["value"]
        self.ALL_DUO_AVG_TIME_PER_GAME = self.parsed["stats"]["p10"]["avgTimePlayed"]["value"]

        self.ALL_SQUAD_WINS = self.parsed["stats"]["p9"]["top1"]["value"]
        self.ALL_SQUAD_TOP3 = self.parsed["stats"]["p9"]["top3"]["value"]
        self.ALL_SQUAD_TOP5 = self.parsed["stats"]["p9"]["top6"]["value"]
        self.ALL_SQUAD_TOP6 = self.parsed["stats"]["p9"]["top6"]["value"]
        self.ALL_SQUAD_TOP10 = self.parsed["stats"]["p9"]["top10"]["value"]
        self.ALL_SQUAD_TOP12 = self.parsed["stats"]["p9"]["top12"]["value"]
        self.ALL_SQUAD_TOP25 = self.parsed["stats"]["p9"]["top25"]["value"]
        self.ALL_SQUAD_KD = self.parsed["stats"]["p9"]["kd"]["value"]
        try:
            self.ALL_SQUAD_WIN_CHANCE = self.parsed["stats"]["p9"]["winRatio"]["value"] + "%"
        except:
            self.ALL_SQUAD_WIN_CHANCE = "0.00%"
        self.ALL_SQUAD_GAMES = self.parsed["stats"]["p9"]["matches"]["value"]
        self.ALL_SQUAD_KILLS = self.parsed["stats"]["p9"]["kills"]["value"]
        self.ALL_SQUAD_KPG = self.parsed["stats"]["p9"]["kpg"]["value"]
        self.ALL_SQUAD_AVG_TIME_PER_GAME = self.parsed["stats"]["p9"]["avgTimePlayed"]["value"]

        self.SOLO_WINS = self.parsed["stats"]["curr_p2"]["top1"]["value"]
        self.SOLO_TOP3 = self.parsed["stats"]["curr_p2"]["top3"]["value"]
        self.SOLO_TOP5 = self.parsed["stats"]["curr_p2"]["top5"]["value"]
        self.SOLO_TOP6 = self.parsed["stats"]["curr_p2"]["top6"]["value"]
        self.SOLO_TOP10 = self.parsed["stats"]["curr_p2"]["top10"]["value"]
        self.SOLO_TOP12 = self.parsed["stats"]["curr_p2"]["top12"]["value"]
        self.SOLO_TOP25 = self.parsed["stats"]["curr_p2"]["top25"]["value"]
        self.SOLO_KD = self.parsed["stats"]["curr_p2"]["kd"]["value"]
        try:
            self.SOLO_WIN_CHANCE = self.parsed["stats"]["curr_p2"]["winRatio"]["value"] + "%"
        except:
            self.SOLO_WIN_CHANCE = "0.00%"
        self.SOLO_GAMES = self.parsed["stats"]["curr_p2"]["matches"]["value"]
        self.SOLO_KILLS = self.parsed["stats"]["curr_p2"]["kills"]["value"]
        self.SOLO_KPG = self.parsed["stats"]["curr_p2"]["kpg"]["value"]
        self.SOLO_AVG_TIME_PER_GAME = self.parsed["stats"]["curr_p2"]["avgTimePlayed"]["value"]

        self.DUO_WINS = self.parsed["stats"]["curr_p10"]["top1"]["value"]
        self.DUO_TOP3 = self.parsed["stats"]["curr_p10"]["top3"]["value"]
        self.DUO_TOP5 = self.parsed["stats"]["curr_p10"]["top6"]["value"]
        self.DUO_TOP6 = self.parsed["stats"]["curr_p10"]["top6"]["value"]
        self.DUO_TOP10 = self.parsed["stats"]["curr_p10"]["top10"]["value"]
        self.DUO_TOP12 = self.parsed["stats"]["curr_p10"]["top12"]["value"]
        self.DUO_TOP25 = self.parsed["stats"]["curr_p10"]["top25"]["value"]
        self.DUO_KD = self.parsed["stats"]["curr_p10"]["kd"]["value"]
        try:
            self.DUO_WIN_CHANCE = self.parsed["stats"]["curr_p10"]["winRatio"]["value"] + "%"
        except:
            self.DUO_WIN_CHANCE = "0.00%"
        self.DUO_GAMES = self.parsed["stats"]["curr_p10"]["matches"]["value"]
        self.DUO_KILLS = self.parsed["stats"]["curr_p10"]["kills"]["value"]
        self.DUO_KPG = self.parsed["stats"]["curr_p10"]["kpg"]["value"]
        self.DUO_AVG_TIME_PER_GAME = self.parsed["stats"]["curr_p10"]["avgTimePlayed"]["value"]

        self.SQUAD_WINS = self.parsed["stats"]["curr_p9"]["top1"]["value"]
        self.SQUAD_TOP3 = self.parsed["stats"]["curr_p9"]["top3"]["value"]
        self.SQUAD_TOP5 = self.parsed["stats"]["curr_p9"]["top6"]["value"]
        self.SQUAD_TOP6 = self.parsed["stats"]["curr_p9"]["top6"]["value"]
        self.SQUAD_TOP10 = self.parsed["stats"]["curr_p9"]["top10"]["value"]
        self.SQUAD_TOP12 = self.parsed["stats"]["curr_p9"]["top12"]["value"]
        self.SQUAD_TOP25 = self.parsed["stats"]["curr_p9"]["top25"]["value"]
        self.SQUAD_KD = self.parsed["stats"]["curr_p9"]["kd"]["value"]
        try:
            self.SQUAD_WIN_CHANCE = self.parsed["stats"]["curr_p9"]["winRatio"]["value"] + "%"
        except:
            self.SQUAD_WIN_CHANCE = "0.00%"
        self.SQUAD_GAMES = self.parsed["stats"]["curr_p9"]["matches"]["value"]
        self.SQUAD_KILLS = self.parsed["stats"]["curr_p9"]["kills"]["value"]
        self.SQUAD_KPG = self.parsed["stats"]["curr_p9"]["kpg"]["value"]
        self.SQUAD_AVG_TIME_PER_GAME = self.parsed["stats"]["curr_p9"]["avgTimePlayed"]["value"]
        
        self.TOTAL_WINS = self.parsed["lifeTimeStats"][8]["value"]
        self.TOTAL_MATCHES_PLAYED = self.parsed["lifeTimeStats"][7]["value"]
        self.TOTAL_WIN_CHANCE = self.parsed["lifeTimeStats"][9]["value"] + "%"
        self.TOTAL_KILLS = self.parsed["lifeTimeStats"][10]["value"]
        self.TOTAL_KD = self.parsed["lifeTimeStats"][11]["value"]
        self.TOTAL_KILLS_PER_MIN = self.parsed["lifeTimeStats"][12]["value"]
        self.TOTAL_TIME_PLAYED = self.parsed["lifeTimeStats"][13]["value"]
        self.TOTAL_AVG_GAME_TIME = self.parsed["lifeTimeStats"][14]["value"]
