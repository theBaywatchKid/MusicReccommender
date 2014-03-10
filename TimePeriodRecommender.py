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
 
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km 

numUsers = 1
average = 0 
zeroCounter = 0
#pwd = getpass()
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwave", 
                     cursorclass=MySQLdb.cursors.DictCursor) 



insertChecker = {}
userChecker = {}
Similarity = []
currentItemList = []
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
countCursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
countCursor.execute("select songid from actions where type = 'play' and time between '2013-08-02' and '2013-08-09' ;")
countCursorResults = countCursor.fetchall()
#avgChecker = []
for res in countCursorResults:
    heappush(Similarity, res['songid'])
    

songList = {}
for count in range(len(Similarity)):
    item = heappop(Similarity)
    if item in songList:
        songList[item] += 1
    else:
        songList[item] = 1
  

song = []
song =  sorted(songList, key=songList.get, reverse=True)
for n in range(15):
    curSong.execute("Select artist, title from songs where songid = %s;", song[n])
    resultSong = curSong.fetchall()
    for resSong in resultSong:
       
        if song[n] == 359:
            print "The system reccommends : Radioactive by {0}".format(  resSong['artist'])
        else:
            print "The system reccommends : {0} by {1}".format( resSong['title'] , resSong['artist'])
 
db.close()    