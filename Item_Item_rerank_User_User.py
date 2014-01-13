from scipy.sparse import lil_matrix
from scipy import spatial
import heapq
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.cross_validation import train_test_split
from collections import Counter
from random import shuffle
import MySQLdb
import math
import MySQLdb.cursors
from operator import itemgetter
from heapq import heappush, heappop, heappushpop

numItems = 120000 
numUsers = 42000
userId = 1

songId = int(raw_input('Please type a song Id: '))
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwave", 
                     cursorclass=MySQLdb.cursors.DictCursor) 

                     
itemMatrix = lil_matrix((120000, 42000))
userMatrix = lil_matrix((42000, 120000))

userCur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
currentSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = cur.fetchall()
for row in rows:
    itemMatrix[row['songid'],row['userid']] = 1 

userCur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = userCur.fetchall()
for row in rows:
    userMatrix[row['userid'],row['songid']] = 1 
    
print "Matrix set up." 

Similarity = []
candidateList = []
currentItemMatrix = itemMatrix.getrowview(songId)      
for j in range(1, numItems):
    tempItemMatrix = itemMatrix.getrowview(j) 
    if j != songId:
        if j <= 10:
            temp = cosine_similarity(currentItemMatrix, tempItemMatrix)
            heappush(Similarity, ( temp[0][0], j ))
        else:    
            temp = cosine_similarity(currentItemMatrix, tempItemMatrix)
            if temp[0][0] > Similarity[0][0]:
                heappushpop(Similarity, ( temp[0][0], j))

for index in range(len(Similarity)):
    temp = heappop(Similarity)
    candidateList.append(temp[1])
    
for n in range(len(candidateList)):
    curSong.execute("Select artist, title from songs where songid = %s;", int(candidateList[((len(candidateList)-1)-n)]))
    resultSong = curSong.fetchall()
    for resSong in resultSong:
        print "The system initially reccommends songs : {0} by {1} ".format(resSong['title'] , resSong['artist'])

inList = False
userSimilarity = []
count = 0
currentUserMatrix = userMatrix.getrowview(userId)    
for j in range(1, numUsers):
    tempUserMatrix = userMatrix.getrowview(j)
    tempUserList = tempUserMatrix.rows[0]
    for listItem in tempUserList:
        if listItem in candidateList:
            inList = True
            break
    if inList == True:    
        if userId != j:
            if count <= 26:
                temp = cosine_similarity(currentUserMatrix, tempUserMatrix)
                heappush(userSimilarity, ( temp[0][0], j ))
                count += 1
            else:    
                temp = cosine_similarity(currentUserMatrix, tempUserMatrix)
                if temp[0][0] > userSimilarity[0][0]:
                    heappushpop(userSimilarity, ( temp[0][0], j))
        inList = False           
currentUserMatrix = userMatrix.getrow(userId) 
currentUserList = currentUserMatrix.rows[0] 

songList = {}
for count in range(len(userSimilarity)):
    user = heappop(userSimilarity)
    tempUserMatrix = userMatrix.getrow(user[1]) 
    tempUserList = tempUserMatrix.rows[0]
    for item in tempUserList:
        if item in songList:
            songList[item] += user[0]
        else:
            songList[item] = user[0]    

song = []
song =  sorted(songList, key=songList.get, reverse=True)

relevantSongs = [x for x in song if x in candidateList]

currentSong.execute("Select artist, title from songs where songid = %s;", int(songId))
result = currentSong.fetchall()
for res in result:
    print "These reccommendations are based on song: {0} by {1}".format(res['title'] , res['artist'])
#print song

for n in range(len(relevantSongs)):
    curSong.execute("Select artist, title from songs where songid = %s;", int(relevantSongs[n]))
    resultSong = curSong.fetchall()
    for resSong in resultSong:
        print "The reranked system reccommends song : {0} by {1} ".format(resSong['title'] , resSong['artist'])


db.close()    