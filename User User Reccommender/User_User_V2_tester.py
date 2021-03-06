from __future__ import division
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
import matplotlib.pyplot as pyplot
 

numUsers = 42000
average = 0 
zeroCounter = 0
#pwd = getpass()
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwave", 
                     cursorclass=MySQLdb.cursors.DictCursor) 

trainMatrix = lil_matrix((42000, 120000))
testMatrix = lil_matrix((42000, 120000))

insertChecker = {}
userChecker = {}

countCursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
countCursor.execute("SELECT userid, count(userid) as cnt from actions group by userid;");
countCursorResults = countCursor.fetchall()
#avgChecker = []
for res in countCursorResults:
    insertChecker[res['userid']] = res['cnt']
   # avgChecker.append(res['cnt'])
    userChecker[res['userid']] = 0
# pyplot.plot(avgChecker) 
# pyplot.savefig('example01.png') 
# print "average user", sum(avgChecker)/float(len(avgChecker))
# arr = np.array(avgChecker)
# print "std dev", np.std(avgChecker, axis=0)



cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = cur.fetchall()
for row in rows:
    if userChecker[row['userid']] < (insertChecker[row['userid']]*0.7):
        trainMatrix[row['userid'],row['songid']] = 1; 
        userChecker[row['userid']] += 1
    else:
        testMatrix[row['userid'],row['songid']] = 1;    

print "Matrix set up." 

for i in range(1, 1000):
    Similarity= []
    count = 0
    currentUserMatrix = trainMatrix.getrowview(i)  
    currentUserList = currentUserMatrix.rows[0]  
    for j in range(1, 42000):
        tempUserMatrix = trainMatrix.getrowview(j)
        tempUserList = tempUserMatrix.rows[0]
        for item in tempUserList:
            if item in currentUserList:
                check = True
                break
        if check == True:    
            if i != j:
                if count <= 26:
                    temp = cosine_similarity(currentUserMatrix, tempUserMatrix)
                    heappush(Similarity, ( temp[0][0], j ))
                    count += 1
                else:    
                    temp = cosine_similarity(currentUserMatrix, tempUserMatrix)
                    if temp[0][0] > Similarity[0][0]:
                        heappushpop(Similarity, ( temp[0][0], j))
            check = False            
    currentUserMatrix = trainMatrix.getrow(i) 
    currentUserList = currentUserMatrix.rows[0] 
    
    songList = {}
    for count in range(len(Similarity)):
        user = heappop(Similarity)
        tempUserMatrix = trainMatrix.getrow(user[1]) 
        tempUserList = tempUserMatrix.rows[0]
        for item in tempUserList:
            if item not in currentUserList:
                if item in songList:
                    songList[item] += user[0]
                else:
                    songList[item] = user[0]    
    
    song = []
    song =  sorted(songList, key=songList.get, reverse=True)
#     for n in range(len(song)):
#         curSong.execute("Select artist, title from songs where songid = %s;", song[n])
#         resultSong = curSong.fetchall()
#         for resSong in resultSong:
#             print "The system reccommends user {0} : {1} by {2}".format(i, resSong['title'] , resSong['artist'])
    currentUsertestMatrix = testMatrix.getrowview(i)  
    currentUsertestList = currentUsertestMatrix.rows[0] 
    answer = 0
    numSongsInOrigList = [x for x in song if x in currentUsertestList]
    if len(currentUsertestList) > 0 and len(numSongsInOrigList) > 0:
        answer = len(numSongsInOrigList) / len(currentUsertestList)
    else:
        zeroCounter+=1
    
    average += answer
    print"The accuracy of this reccommendation was:", answer
print "Average", float(average)/1000
print "zeros", zeroCounter    
db.close()    