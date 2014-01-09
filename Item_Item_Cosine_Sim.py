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

numItems = 120000 

#pwd = getpass()
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwaveLocation", 
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
                     
matrix = lil_matrix((120000, 42000))

cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = cur.fetchall()
for row in rows:
    matrix[row['songid'],row['userid']] = 1 

print "Matrix set up." 

for k in range(1, 1000):
    currentUserMatrix = userMatrix.getrow(k)	
    currentList = currentUserMatrix.rows[0]
    
    topItems = []
    for i in range( len(currentList)):
	Similarity = {}
	currentUserMatrix = matrix.getrow(currentList[i])	  
	for j in range(1, numItems):
	    tempUserMatrix = matrix.getrow(j)
	    if i == j:
		Similarity[j] = 0
	    else:
		if len(currentUserMatrix.rows[0]) >= 20:
		    Similarity[j] = cosine_similarity(currentUserMatrix, tempUserMatrix)
		else:
		    Similarity[j] = (cosine_similarity(currentUserMatrix, tempUserMatrix)/20)

	
	topItems += heapq.nlargest(2, Similarity, key=Similarity.get)
	#print "Top users", topUsers
	
	print "Top items", topItems
	
	
	#print finalList
	
    currentUserMatrix = matrix.getrow(k) 
    currentUserList = currentUserMatrix.rows[0]    
	
    finalSong = [x for x in topItems if x not in currentUserList] 
    
    #print finalSong
    
    c = Counter(finalSong)
    song =  c.most_common(10)  
    #print song
    for item in range(len(song)):
	songId = song[item][0]
	curSong.execute("Select artist, title from songs where songid = %s;", int(songId))
	resultSong = curSong.fetchall()
	for resSong in resultSong:
	    print "The system reccommends user {0} : {1} by {2}".format(k, resSong['title'] , resSong['artist'])
	
db.close()	