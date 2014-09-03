from __future__ import division
from scipy.sparse import lil_matrix, csr_matrix
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
resultMatrix = lil_matrix((42000, 120000))

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

for i in range(1, 42000):
    print i
    Similarity= []
    count = 0
    currentUserMatrix = trainMatrix.getrowview(i)  
    currentUserList = currentUserMatrix.rows[0]  
    for j in range(i, 42000):
        tempUserMatrix = trainMatrix.getrowview(j)
        tempUserList = tempUserMatrix.rows[0]
        for item in tempUserList:
            if item in currentUserList:
                check = True
                break
        if check == True:    
            if i != j:
                    temp = cosine_similarity(currentUserMatrix, tempUserMatrix)
                    resultMatrix[i,j] = temp[0][0]
                    count += 1
        else:
            resultMatrix[i,j] = 0            
        check = False            

csrMat = resultMatrix.tocsr()

print resultMatrix.getrowview(2)

np.save("dataArray", csrMat.data)
np.save("indArray", csrMat.indices)
np.save("ptrArray", csrMat.indptr)
dataArray = np.load("dataArray.npy")
indArray =np.load("indArray.npy")
ptrArray = np.load("ptrArray.npy")

new_csr = csr_matrix((dataArray, indArray, ptrArray), shape=(42000,42000))

print new_csr.getrow(2)