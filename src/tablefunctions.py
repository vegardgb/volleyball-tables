import pandas as pd

#Create list of the teams for top leagues in Norway
H0=["NTNUI","OSI",'Viking','Forde','Tromso','Koll','Asker','Randaberg']
D0=['Skjetten','Oslo','Viking','Forde','Tromso','Koll','Volda','Randaberg']
H1=["Askim","Viking 2","Forde 2","NTNUI 2","OSI 2", "Spirit Lørenskog","BTSI","Sotra","Tromso 2","Sandnes"]
D1=["Koll 2","Viking 2","Lierne","NTNUI","OSI","BSI","OKSIL","Tromso 2","Sandnes"]

class Team(object):
    pos = 0
    name = ''
    played = 0
    won = 0
    lost = 0
    setWon = 0
    setLost = 0
    points = 0
    def __init__(self, name):
        self.name = str(name)
    def __eq__(self, other):
        return self.points == other.points and (self.setWon - self.setLost == other.setWon - other.setLost)

    def __lt__(self, other):
        if self.points > other.points:
            return True
        if self.points < other.points:
            return False
        if ((self.setWon - self.setLost) > (other.setWon - other.setLost)):
           return True
        if ((self.setWon - self.setLost) < (other.setWon - other.setLost)):
            return False
        return self.points > other.points

##### FUNCTIONS
        

#Input matchID (line in CSV). Output: teams and scores
def readMatch(matchID):
    match: pd.DataFrame = pd.read_csv("matchlist.csv",skiprows=lambda x: (x != 0) and (x not in range(matchID+1,matchID+2)))
    print(match)
    return str(match.teamA), str(match.teamB), int(match.scoreA), int(match.scoreB)

# Input team name and table, returns position of team in table    
def findPosition(team,table):
    for i in range(len(table)):
        if(str(table[i].name) == str(team)):
            return i
    print('ERROR: Unable to find position of team ' + str(team))

def updateMatch(table,matchID):
    teamA, teamB, scoreA, scoreB = readMatch(matchID)
    teamA = teamA[5:].split("\n",1)[0]
    teamB = teamB[5:].split("\n",1)[0]
    pointsA, pointsB, homeWin = awardPoints(scoreA,scoreB)
    print(pointsB)
    posA = findPosition(teamA,table)
    posB = findPosition(teamB,table)
    table[posA].points += pointsA
    table[posB].points += pointsB
    table[posA].played += 1
    table[posB].played += 1
    if homeWin:
        table[posA].won += 1
        table[posB].lost += 1
    else:
        table[posA].lost += 1
        table[posB].won += 1
    table[posA].setWon += scoreA
    table[posA].setLost += scoreB
    table[posB].setWon += scoreB
    table[posB].setLost += scoreA
    print('Match data for ' + teamA + ' vs ' + teamB + ' successfully updated to table')
    return table

#Update N matches at once calling updateMatch()
def updateMatches(table,N):
    for i in range(N):
        table = updateMatch(table,i)
    return sortTable(table)

# input set scores 
# returns points home, points away, and bool for home win
def awardPoints(scoreA,scoreB):
    if (scoreA == 3):
        win = 1
        if (scoreB < 2):
            pointA = 3
            pointB = 0
        else:
            pointA = 2
            pointB = 1
    else:
        win = 0
        if (scoreA < 2):
            pointA = 0
            pointB = 3
        else:
            pointA = 1
            pointB = 2
    return pointA, pointB,win


# Creates table for table key
def makeTable(league):
    table = []
    for team in league:
        table.append(Team(team))
    for i in range(len(table)):
        table[i].pos=i
    return table
        
def sortTable(table):
    wrongRankTable = sorted(table)
    for i in range (len(table)):
        wrongRankTable[i].pos=i
    return wrongRankTable

#input table, output latex tabular code
# TODO: Add 1st division table
def displayTable(table,Elite=True): 
    col = ' & '
    lineList= []
    lineList.append(r'\textbf{Nr}' + col + 'Lag' + col + 'Spelt' + col +'Vunne' + col + 'Tapt' + col + 'Settskilnad' + col + r'\textbf{Poeng} \\ \gull')
    output = lineList[0]
    for team in table:
        lineList.append(str(team.pos+1) + col + str(team.name) + col + str(team.won+team.lost) + col + str(team.won) + col + str(team.lost) + col + 
                            str(team.setWon)+'-'+str(team.setLost) + col + r'\textbf{'+str(team.points) +r'} \\')
    if Elite:
        output += lineList[1] + r' \solv ' + lineList[2] + r' \bronse ' 
        for i in range(3,7):
            output += lineList[i]
        output += r' \kvalik ' + lineList[7] + r' \nedrykk ' + lineList[8]
        print( output)
    else:
        return 'ERROR: Does not yet support 1st division mode'

def main(N,league):
    table = makeTable(league)
    sortedTable = updateMatches(table,N)
    displayTable(sortedTable)
    
if __name__=="__main__": 
    main(0,H0)
    main(0,D0)