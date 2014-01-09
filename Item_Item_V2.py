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

numItems = 120000 

#pwd = getpass()
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwave", 
                     cursorclass=MySQLdb.cursors.DictCursor) 

userMatrix = lil_matrix((42000, 120000))
countCursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
countCursor.execute("SELECT userid, count(userid) from actions group by userid;");

countCursorResults = countCursor.fetchall()
curOrig = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curOrig.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rowsOrig = curOrig.fetchall()
for rowOrig in rowsOrig:
    userMatrix[rowOrig['userid'],rowOrig['songid']] = 1 
                     
itemMatrix = lil_matrix((120000, 42000))

cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = cur.fetchall()
for row in rows:
    itemMatrix[row['songid'],row['userid']] = 1 

print "Matrix set up." 


for k in range(1, 42000):
    
    currentUserMatrix = userMatrix.getrowview(k)    
    currentUserList = currentUserMatrix.rows[0]
    

    for i in range( len(currentUserList)):
        Similarity = {}
        currentItemMatrix = itemMatrix.getrowview(currentUserList[i])      
        for j in range(1, numItems):
            tempItemMatrix = itemMatrix.getrowview(j)
            if i != j:
                if j <= 26:
                    temp = cosine_similarity(currentItemMatrix, tempItemMatrix)
                    heappush(Similarity, ( temp[0][0], j ))
                else:    
                    temp = cosine_similarity(currentItemMatrix, tempItemMatrix)
                    if temp[0][0] > Similarity[0][0]:
                        heappushpop(Similarity, ( temp[0][0], j))
                  

    

    
    
    songList = {}
    for count in range(25):
        item = heappop(Similarity)
        itemMatrix = itemMatrix.getrowview(item[1]) 
        itemList = tempUserMatrix.rows[0]
        for item in itemList:
            if item not in currentUserList:
                if item in songList:
                    songList[item] += item[0]
                else:
                    songList[item] = item[0]    
    
    
    for song in sorted(songList, key=songList.get, reverse=True):
        curSong.execute("Select artist, title from songs where songid = %s;", song)
        resultSong = curSong.fetchall()
        for resSong in resultSong:
            print "The system reccommends user {0} : {1} by {2}".format(i, resSong['title'] , resSong['artist'])
    
db.close()    