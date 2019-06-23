import requests
import ast
from lxml import html

def initTeam(team):
    teamTotals[team] = dict({'wins': 0, 'losses': 0, 'ties': 0, 'name': '', 'tourneys': 0, 'qf': 0, 'sf': 0, 'finals': 0, 'champs': 0, 'power': 0, 'sos': 0})

def sortTeams(team1, team2):
    team1Score = teamTotals[team1]['sos']
    team2Score = teamTotals[team2]['sos']

    if (team1Score > team2Score):
        return -1
    elif (team1Score == team2Score):
        return 0
    else:
        return 1

def scrapeTeamNames(tourney):
    page = requests.get(tourney)
    tree = html.fromstring(page.content)

    rawData = str(tree.xpath('//div[@id="matchResults"]/div[1]/div[2]/div/div[2]/rankings/@data')[0])
    data = ast.literal_eval(rawData)

    for team_results in data:
        teamNumber = team_results['teamnum']
        if teamNumber not in teamTotals:
            initTeam(teamNumber)
            teamTotals[teamNumber]['name'] = team_results['teamname']

        teamTotals[teamNumber]['tourneys'] += 1

def processTeams(teamList, oppTeamList, score1, score2, round):
    for team in teamList:
        if team not in teamTotals:
            initTeam(team)

        if (round > 0):
            if (score1 > score2):
                teamTotals[team]['wins'] += 1
            elif (score1 < score2):
                teamTotals[team]['losses'] += 1
                if (round == 6): round -= 1
            else:
                teamTotals[team]['ties'] += 1
        else:
            oppStrength = (teamTotals[oppTeamList[0]]['winpct'] + teamTotals[oppTeamList[1]]['winpct']) / 2
            allyStrength = (teamTotals[teamList[0]]['winpct'] + teamTotals[teamList[1]]['winpct'] - teamTotals[team]['winpct'])
            teamTotals[team]['sos'] += (2 * oppStrength - 2 * allyStrength)

def calcWinPct():
    for team in teamTotals:
        teamTotals[team]['winpct'] = (float) (2 * teamTotals[team]['wins'] + teamTotals[team]['ties']) / \
                                     (2 * (teamTotals[team]['wins'] + teamTotals[team]['losses'] + teamTotals[team]['ties']))

tourneyFileName = raw_input("Enter tournament file: ")
maxRound = int(raw_input("Enter highest round (2 = qualifiers, 5 = finals):"))

# Open file "VEX Tournaments" and read in event URLs line by line
with open(tourneyFileName) as tourneyFile:
    tourneyList = tourneyFile.readlines()

tourneyList = [i.strip() for i in tourneyList]

teamTotals = {}

for tourney in tourneyList:
    page = requests.get(tourney)
    tree = html.fromstring(page.content)

    rawData = str(tree.xpath('//div[@id="matchResults"]/div[1]/div[2]/div/div[1]/*[2]/@data')[0])
    data = ast.literal_eval(rawData)

    scrapeTeamNames(tourney)

    for match in data:
        def filterSit(item):
            return (item != sittingTeam)

        redScore = match['redscore']
        blueScore = match['bluescore']

        sittingTeam = match['redsit']
        redTeams = filter(filterSit, filter(len, [match['red1'], match['red2'], match['red3']]))
        sittingTeam = match['bluesit']
        blueTeams = filter(filterSit, filter(len, [match['blue1'], match['blue2'], match['blue3']]))

        round = match['round']
        if (round <= maxRound):
            if (match == data[-1]): round = 6

            processTeams(redTeams, blueTeams, redScore, blueScore, round)
            processTeams(blueTeams, redTeams, blueScore, redScore, round)

calcWinPct()

for tourney in tourneyList:
    page = requests.get(tourney)
    tree = html.fromstring(page.content)

    rawData = str(tree.xpath('//div[@id="matchResults"]/div[1]/div[2]/div/div[1]/*[2]/@data')[0])
    data = ast.literal_eval(rawData)

    for match in data:
        def filterSit(item):
            return (item != sittingTeam)

        redScore = match['redscore']
        blueScore = match['bluescore']

        sittingTeam = match['redsit']
        redTeams = filter(filterSit, filter(len, [match['red1'], match['red2'], match['red3']]))
        sittingTeam = match['bluesit']
        blueTeams = filter(filterSit, filter(len, [match['blue1'], match['blue2'], match['blue3']]))

        if (match['round'] <= maxRound):
            round = 0

            processTeams(redTeams, blueTeams, redScore, blueScore, round)
            processTeams(blueTeams, redTeams, blueScore, redScore, round)

rankedTeams = teamTotals.keys()
rankedTeams.sort(sortTeams)

for team in rankedTeams:
    print team, ", (", teamTotals[team]['name'], "), ", teamTotals[team]['wins'], ",", teamTotals[team]['losses'], ",", teamTotals[team]['ties'], \
        ", ", teamTotals[team]['tourneys'], ",", teamTotals[team]['qf'], ",", teamTotals[team]['sf'], ",", teamTotals[team]['finals'], \
        ",", teamTotals[team]['champs'], ",", teamTotals[team]['power'] / (teamTotals[team]['wins'] + teamTotals[team]['losses'] + teamTotals[team]['ties']) , ", ", teamTotals[team]['sos']