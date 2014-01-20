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
import scipy.stats

numItems = 120000 
numUsers = 42000
userId = 1


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
totalResults = []

for songId in range(1, 100):
    currentSong.execute("Select artist, title from songs where songid = %s;", int(songId))
    result = currentSong.fetchall()
    for res in result:
        print "These reccommendations are based on song: {0} by {1}".format(res['title'] , res['artist'])
        
    Similarity = []
    count = 0
    check = None
    candidateList = []
    currentItemMatrix = itemMatrix.getrowview(songId) 
    currentItemList = currentItemMatrix.rows[0]     
    for j in range(1, numItems):
        tempItemMatrix = itemMatrix.getrowview(j)
        tempItemList = tempItemMatrix.rows[0]
        for item in tempItemList:
            if item in currentItemList:
                check = True
                break
        if check == True:
            if count <= 26:
                temp = cosine_similarity(currentItemMatrix, tempItemMatrix)
                heappush(Similarity, ( temp[0][0], j ))
                count+=1
            else:    
                temp = cosine_similarity(currentItemMatrix, tempItemMatrix)
                if temp[0][0] > Similarity[0][0]:
                    heappushpop(Similarity, ( temp[0][0], j))
            check = False
    
    for index in range(len(Similarity)):
        temp = heappop(Similarity)
        if temp[1] != songId:
            candidateList.append(temp[1])
        

    finalList = {}
    for k in range(len(candidateList)):
        runningTotal = 0
        inList = False
        userSimilarity = []
        count = 0
        currentUserMatrix = userMatrix.getrowview(userId)    
        for j in range(1, numUsers):
            tempUserMatrix = userMatrix.getrowview(j)
            tempUserList = tempUserMatrix.rows[0]
            if candidateList[k] in tempUserList:
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
    
        for count in range(len(userSimilarity)):
            user = heappop(userSimilarity)
            runningTotal += user[0] 
        
        finalList[candidateList[k]] = runningTotal
              
    
    song = []
    song =  sorted(finalList, key=finalList.get, reverse=True)
    
    spearmanResult = scipy.stats.spearmanr(candidateList, song)
    if abs(spearmanResult[0]) != []:
        print "Spearman relation coefficient for reranking :", abs(spearmanResult[0])
        totalResults.append(abs(spearmanResult[0]))
sum = 0    
for x in totalResults:
    sum += float(x)    
average = sum / len(totalResults) 
print "Average Spearman relation coefficient", average   
db.close()    