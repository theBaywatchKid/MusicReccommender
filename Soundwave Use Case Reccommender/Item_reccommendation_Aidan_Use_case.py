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

songId = int(raw_input('Please type a song Id: '))
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwave", 
                     cursorclass=MySQLdb.cursors.DictCursor) 

                     
itemMatrix = lil_matrix((120000, 42000))

cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
currentSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = cur.fetchall()
for row in rows:
    itemMatrix[row['songid'],row['userid']] = 1 

print "Matrix set up." 

Similarity = []
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


print Similarity

currentSong.execute("Select artist, title from songs where songid = %s;", int(songId))
result = currentSong.fetchall()
for res in result:
    print "These reccommendations are based on song: {0} by {1}".format(res['title'] , res['artist'])
#print song

for n in range(len(Similarity)):
    song = heappop(Similarity)
    curSong.execute("Select artist, title from songs where songid = %s;", song[1])
    resultSong = curSong.fetchall()
    for resSong in resultSong:
	print "The system reccommends song : {0} by {1} ".format(resSong['title'] , resSong['artist'])

db.close()	