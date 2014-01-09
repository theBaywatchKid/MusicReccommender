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

numUsers = 42000 

#pwd = getpass()
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwaveLocation", 
                     cursorclass=MySQLdb.cursors.DictCursor) 

matrix = lil_matrix((42000, 120000))

cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = cur.fetchall()
for row in rows:
    matrix[row['userid'],row['songid']] = 1; 

print "Matrix set up." 

for i in range(1, 1000):
    Similarity = {}
    currentUserMatrix = matrix.getrow(i)
    if len(currentUserMatrix.rows[0]) < 20:
	print "User %d has played less than 20 tracks."% i
    else:	  
	for j in range(1, numUsers):
	    tempUserMatrix = matrix.getrow(j)
	    if i == j:
		Similarity[j] = 0
	    else:
		if len(currentUserMatrix.rows[0]) >= 20:
		    Similarity[j] = cosine_similarity(currentUserMatrix, tempUserMatrix)
		else:
		    Similarity[j] = (cosine_similarity(currentUserMatrix, tempUserMatrix)/20)

	
	topUsers = heapq.nlargest(25, Similarity, key=Similarity.get)
	#print "Top users", topUsers
	
	finalList = []
	for count in range(25):
	    currentTempMatrix = matrix.getrow(topUsers[count]) 
	    finalList += currentTempMatrix.rows[0]
	
	#print finalList
	
	currentUserMatrix = matrix.getrow(i) 
	currentUserList = currentUserMatrix.rows[0]    
	    
	finalSong = [x for x in finalList if x not in currentUserList] 
	
	#print finalSong
	
	c = Counter(finalSong)
	song =  c.most_common(5)  
	#print song
	for item in range(len(song)):
	    songId = song[item][0]
	    curSong.execute("Select artist, title from songs where songid = %s;", int(songId))
	    resultSong = curSong.fetchall()
	    for resSong in resultSong:
		print "The system reccommends user {0} : {1} by {2}".format(i, resSong['title'] , resSong['artist'])
	
db.close()	