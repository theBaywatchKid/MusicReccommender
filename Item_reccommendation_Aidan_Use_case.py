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

numItems = 120000 

songId = int(raw_input('Please type a song Id: '))
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwave", 
                     cursorclass=MySQLdb.cursors.DictCursor) 

                     
matrix = lil_matrix((120000, 42000))

cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
currentSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = cur.fetchall()
for row in rows:
    matrix[row['songid'],row['userid']] = 1 

print "Matrix set up." 

topItems = []

Similarity = {}
currentUserMatrix = matrix.getrow(songId)	  
for j in range(1, numItems):
    tempUserMatrix = matrix.getrow(j)
    if songId == j:
	    Similarity[j] = 0
    else:
	if len(currentUserMatrix.rows[0]) >= 20:
	    Similarity[j] = cosine_similarity(currentUserMatrix, tempUserMatrix)
	else:
	    Similarity[j] = (cosine_similarity(currentUserMatrix, tempUserMatrix)/20)


topItems = heapq.nlargest(5, Similarity, key=Similarity.get)
#print "Top users", topUsers

print "Top items", topItems


#print finalList    
#print finalSong
currentSong.execute("Select artist, title from songs where songid = %s;", int(songId))
result = currentSong.fetchall()
for res in result:
    print "These reccommendations are based on song: {0} by {1}".format(res['title'] , res['artist'])
#print song
for item in topItems:
    curSong.execute("Select artist, title from songs where songid = %s;", int(item))
    resultSong = curSong.fetchall()
    for resSong in resultSong:
	print "The system reccommends song : {0} by {1} ".format(resSong['title'] , resSong['artist'])

db.close()	