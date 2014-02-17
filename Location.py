from scipy import spatial
import heapq
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter
from random import shuffle
import MySQLdb
import math
import MySQLdb.cursors
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

import haversine

db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwaveBig", 
                     cursorclass=MySQLdb.cursors.DictCursor) 


cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT userid, lon, lat from actions where userid = 2;");

cursorResults = cur.fetchall()
resultList = []
for rowOrig in cursorResults:
    if rowOrig['lon'] != 0 :
        temp = rowOrig['lon'], rowOrig['lat']
        resultList.append(temp)
         
for i in range(len(resultList) -1):
    temp1 = resultList[i]
    temp2 = resultList[i+1]
    
    print haversine.distance(temp1, temp2)
    
    