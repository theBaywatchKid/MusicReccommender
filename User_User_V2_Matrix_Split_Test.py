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
from getpass import getpass
from operator import itemgetter
from heapq import heappush, heappop, heappushpop
numUsers = 42000 

db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwave", 
                     cursorclass=MySQLdb.cursors.DictCursor) 

matrix = lil_matrix((42000, 120000))

cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = cur.fetchall()
for row in rows:
    matrix[row['userid'],row['songid']] = 1; 
    
matrixTrain, matrixTest = train_test_split(matrix, test_size=0.3, random_state=42)

print "Matrix set up." 

for i in range(4, 42000):
    Similarity= []
    currentUserMatrix = matrixTrain.getrow(i)    
    for j in range(1, numUsers):
        tempUserMatrix = matrixTrain.getrow(j)
        if i != j:
            if j <= 26:
                temp = cosine_similarity(currentUserMatrix, tempUserMatrix)
                heappush(Similarity, ( temp[0][0], j ))
            else:    
                temp = cosine_similarity(currentUserMatrix, tempUserMatrix)
                if temp[0][0] > Similarity[0][0]:
                    heappushpop(Similarity, ( temp[0][0], j))
                  
    currentUserMatrix = matrixTrains.getrow(i) 
    currentUserList = currentUserMatrix.rows[0] 
    
    songList = {}
    for count in range(25):
        user = heappop(Similarity)
        tempUserMatrix = matrixTrain.getrow(user[1]) 
        tempUserList = tempUserMatrix.rows[0]
        for item in tempUserList:
            if item not in currentUserList:
                if item in songList:
                    songList[item] += user[0]
                else:
                    songList[item] = user[0]    
    
    song = []
    song =  sorted(songList, key=songList.get, reverse=True)
    
    testUserMatrix = matrixTest.getrow(i) 
    testUserList = testUserMatrix.rows[0] 
    for n in testUserList:
        if n in song:   
            ratio +=1
    result = ratio / len(textUserList)        
    
    print "The accuracy of these recccommendations was ", result  
        
#         curSong.execute("Select artist, title from songs where songid = %s;", song[n])
#         resultSong = curSong.fetchall()
#         for resSong in resultSong:
#             print "The system reccommends user {0} : {1} by {2}".format(i, resSong['title'] , resSong['artist'])
    
db.close()    