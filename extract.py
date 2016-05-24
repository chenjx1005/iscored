import requests
import json

headers = {
	'accept': 'application/json, text/javascript, */*; q=0.01',
	'accept-encoding': 'gzip, deflate, sdch',
	'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
	'cookie': 'visid_incap_774904=LCtv2wUZQVypnnLhb/U/WqrBQlcAAAAAQUIPAAAAAACXiuWhXGMYozNA8X5lteMW; incap_ses_407_774904=USLQUjcvS3bPiZC13PSlBavBQlcAAAAAAvo+BAtZ4/RYc7rrZvq9OA==; incap_ses_266_774904=fyTLKOTSbg2Pr0gW1gWxA5AyRFcAAAAAih/vILBtZt1LOj+UMGt1IQ==; _ga=GA1.2.362616800.1464021566; crtg_rta=',
	'model-last-mode': 'wfUgvEZ2/4wlvq99GkiK52Lrq2b9X15hEgI5MDITbJU=',
	'referer': 'https://www.whoscored.com/Matches/958821/LiveStatistics/England-Premier-League-2015-2016-Manchester-United-Bournemouth',
	'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.108 Safari/537.36',
	'x-requested-with': 'XMLHttpRequest',
}

url = 'https://www.whoscored.com/StatisticsFeed/1/GetMatchCentrePlayerStatistics?category=defensive&subcategory=all&statsAccumulationType=0&isCurrent=true&playerId=&teamIds=32&matchId=958821&stageId=&tournamentOptions=&sortBy=&sortAscending=&age=&ageComparisonType=&appearances=&appearancesComparisonType=&field=&nationality=&positionOptions=&timeOfTheGameEnd=&timeOfTheGameStart=&isMinApp=&page=&includeZeroValues=&numberOfPlayersToPick='

r = requests.get(url, headers=headers)

data = r.text.encode('ascii','ignore')

j = json.loads(data)