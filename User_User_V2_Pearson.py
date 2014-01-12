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

#pwd = getpass()
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

print "Matrix set up." 

for i in range(1, 42000):
    Similarity= []
    currentUserMatrix = matrix.getrowview(i)
    currentUserList = currentUserMatrix.rows[0]     
    for j in range(1, numUsers):
        tempUserMatrix = matrix.getrowview(j)
        tempUserList = tempUserMatrix.rows[0] 
        if i != j:
            if j <= 26:
                temp = [x for x in tempUserList if x in currentUserList] 
                print len(temp)
                heappush(Similarity, ((len(temp)//len(currentUserList)), j))
            else:    
                temp = [x for x in tempUserList if x in currentUserList]
                if (len(temp)/len(currentUserList)) > Similarity[0][0]:
                    heappush(Similarity, ((len(temp)//len(currentUserList)), j))
                    
    print Similarity
                  
    currentUserMatrix = matrix.getrow(i) 
    currentUserList = currentUserMatrix.rows[0] 
    
    songList = {}
    for count in range(25):
        user = heappop(Similarity)
        tempUserMatrix = matrix.getrow(user[1]) 
        tempUserList = tempUserMatrix.rows[0]
        for item in tempUserList:
            if item not in currentUserList:
                if item in songList:
                    songList[item] += user[0]
                else:
                    songList[item] = user[0]    
    
    song = []
    song =  sorted(songList, key=songList.get, reverse=True)
    for n in range(25):
        curSong.execute("Select artist, title from songs where songid = %s;", song[n])
        resultSong = curSong.fetchall()
        for resSong in resultSong:
            print "The system reccommends user {0} : {1} by {2}".format(i, resSong['title'] , resSong['artist'])
    
db.close()    