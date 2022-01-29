import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn' # Avoid warnings for dataframe handling

#Create list of the teams for top leagues in Norway
H0=["Asker","Førde","Koll","NTNUI","OSI","Randaberg","Tromsø",'Viking']
D0=['Førde','KFUM Volda','Koll','NTNUI','Oslo Volley','Randaberg','Skjetten','Tromsø','Viking']
H1=["Askim","BTSI","Førde 2","NTNUI 2","OSI 2","Sandnes","Sotra","Spirit Lørenskog","Torvastad","Tromsø 2","Viking 2"]
D1=["BSI","Koll 2","Lierne","NTNUI 2","OSI","Randaberg 2","Sandnes","Tromsø 2","Viking 2"]
league_keys = ['H0','D0','H1','D1']

# Creates team object which can be sorted according to table criteria
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
        return self.points == other.points and self.won == other.won and (self.setWon - self.setLost == other.setWon - other.setLost) and (self.setWon == other.setWon)

    def __lt__(self, other):
        if self.points > other.points:
            return True
        if self.points < other.points:
            return False
        if self.won > other.won:
            return True
        if self.won < other.won:
            return False
        if ((self.setWon - self.setLost) > (other.setWon - other.setLost)):
           return True
        if ((self.setWon - self.setLost) < (other.setWon - other.setLost)):
            return False
        if (self.setWon > other.setWon):
            return True
        if (self.setWon > other.setWon):
            return False
        return self.points > other.points

##### FUNCTIONS
        

#Input matchID (line in CSV). Output: teams and scores
def readMatch(matchID,key):
    match: pd.DataFrame = pd.read_csv("../data/matchlist"+key+".csv",skiprows=lambda x: (x != 0) and (x not in range(matchID+1,matchID+2)),encoding ='utf-8')
    if (type(match.scoreA[0])!=np.int64):
        #print('This match have not been played!')
        return str(match.teamA), str(match.teamB), False, False
    return str(match.teamA), str(match.teamB), int(match.scoreA), int(match.scoreB)

#Main function to generate all matches for a league
def generate_matches(league,N,line=0,outpath='../data/automated_matchlist.csv'):
    df = pd.DataFrame(np.zeros((N**2,4)),columns=['teamA','teamB','scoreA','scoreB'])
    for i in range(N):
        current_team = league[i]
        for j in range(i):
            df,line = generate_double_match_and_go_to_next_line(df,current_team,league[j],line)
        df, line = generate_tvn_match(df,current_team,line)
    df.to_csv(outpath)

#help function for generating both matches between two teams
def generate_double_match_and_go_to_next_line(df,home,away,line):
    df['teamA'][line]= home
    df['teamB'][line]= away
    line+=1
    df['teamA'][line]= away
    df['teamB'][line] = home
    line += 1
    return df, line

#generates match vs tvn for relevant team
def generate_tvn_match(df,team,line):
    df['teamA'][line] = 'TVN'
    df['teamB'][line] = team
    line +=1
    return df, line

# Input team name and table, returns position of team in table    
def findPosition(team,table):
    for i in range(len(table)):
        if(str(table[i].name) == str(team)):
            return i
    print('ERROR: Unable to find position of team ' + str(team))

def updateMatch(table,matchID,key):
    teamA, teamB, scoreA, scoreB = readMatch(matchID,key)
    if (type(scoreA)==bool):
        return table, False
    teamA = teamA[5:].split("\n",1)[0]
    teamB = teamB[5:].split("\n",1)[0]
    pointsA, pointsB, homeWin = awardPoints(scoreA,scoreB)
    if (teamA != 'TVN'): #TVN shall be removed from the table
        posA = findPosition(teamA,table)
        table[posA].points += pointsA
        table[posA].played += 1
        table[posA].setWon += scoreA
        table[posA].setLost += scoreB
        if homeWin:
            table[posA].won += 1
        else:
            table[posA].lost += 1
    posB = findPosition(teamB,table)
    table[posB].points += pointsB
    table[posB].played += 1
    if homeWin:
        table[posB].lost += 1
    else:
        table[posB].won += 1
    table[posB].setWon += scoreB
    table[posB].setLost += scoreA
    #print('Match data for ' + teamA + ' vs ' + teamB + ' successfully updated to table')
    return table, True

#Update N matches at once calling updateMatch()
def updateMatches(table,N,key):
    for i in range(N):
        table,value = updateMatch(table,i,key)
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
def makeTable(key):
    table = []
    if key == 'H0':
        league = H0
    elif key == 'D0':
        league = D0
    elif key == 'H1':
        league = H1
    elif key == 'D1':
        league = D1
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

def saveTableAsCSV(table,filepath):
    table.to_csv(filepath)

#input table, output latex tabular code
def displayTable(key,N): 
    table = makeTable(key)
    sortedTable = updateMatches(table,N,key)
    #saveTableAsCSV(table,key+'.png')
    col = ' & '
    lineList= []
    lineList.append(r'\textbf{Nr}' + col + 'Lag' + col + 'Spelt' + col +'Vunne' + col + 'Tapt' + col + 'Settskilnad' + col + r'\textbf{Poeng} \\ \gull')
    output = lineList[0]
    for team in sortedTable:
        lineList.append(str(team.pos+1) + col + str(team.name) + col + str(team.won+team.lost) + col + str(team.won) + col + str(team.lost) + col + 
                            str(team.setWon)+'-'+str(team.setLost) + col + r'\textbf{'+str(team.points) +r'} \\')
    if (key == 'H0'):
        output += lineList[1] + r' \solv ' + lineList[2] + r' \bronse ' 
        for i in range(3,7):
            output += lineList[i]
        output += r' \kvalik ' + lineList[7] + r' \nedrykk ' + lineList[8]
    elif (key == 'D0'):
        output += lineList[1] + r' \solv ' + lineList[2] + r' \bronse ' 
        for i in range(3,7):
            output += lineList[i]
        output += r' \kvalik ' + lineList[7] + r' \nedrykk ' + lineList[8] + r' \nedrykk ' + lineList[9]
    elif (key == 'H1'):
        output += lineList[1] + r' \kvalik ' + lineList[2] + r' \kvalik'
        for i in range(3,9):
            output += lineList[i]
        output += r' \nedrykk' + lineList[9] + r' \nedrykk ' + lineList[10] + r' \nedrykk ' + lineList[11]
    elif (key == 'D1'):
        output += lineList[1] + r' \kvalik ' + lineList[2] + r' \kvalik'
        for i in range(3,8):
            output += lineList[i]
        output += r' \nedrykk' + lineList[8]+ r' \nedrykk' + lineList[9]
    print(output)

def main():
    total_matches=[64,81,121,81]
    for i in range (4):
        displayTable(league_keys[i],total_matches[i])

if __name__=="__main__": 
    #generate_matches(H0,8,outpath='../data/matchlistH0.csv')
    #generate_matches(D0,9,outpath='../data/matchlistD0.csv')
    #generate_matches(H1,11,outpath='../data/matchlistH1.csv')
    #generate_matches(D1,9,outpath='../data/matchlistD1.csv')
    main()
