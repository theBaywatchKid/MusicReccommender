import scipy as sp
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
from pyechonest import config
from numpy import array,zeros
from math import radians, cos, sin, asin, sqrt
config.ECHO_NEST_API_KEY="ZQMSEM4X59VR36QVL"
import EchoNestTest as en
import SongDetails as sd
import array

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


dbse = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwaveBig", 
                     cursorclass=MySQLdb.cursors.DictCursor) 


cur = dbse.cursor(cursorclass=MySQLdb.cursors.DictCursor)
k = 7 
cur.execute("SELECT userid, lon, lat, songid from actions where type = 'PLAY' and userid = %s;", k);

cursorResults = cur.fetchall()
resultList = []
songList = []
counter = 0
for rowOrig in cursorResults:
    if rowOrig['lon'] != 0 :
        temp = rowOrig['lon'], rowOrig['lat']
        songList.append(rowOrig['songid'])
        resultList.append(temp)
        counter+=1
#print "Result list ", resultList   
resultLoL = [list(elem) for elem in resultList]    
#print resultLoL
ResArray = np.asarray(resultLoL)
#print ResArray

N = ResArray.shape[0]
distance_matrix = zeros((N, N))
for i in xrange(N):
    for j in xrange(N):
        lati, loni = ResArray[i]
        latj, lonj = ResArray[j]
        distance_matrix[i, j] = haversine(loni, lati, lonj, latj)
        distance_matrix[j, i] = distance_matrix[i, j]
        
db = DBSCAN(eps=0.3, min_samples=2, metric="precomputed").fit(distance_matrix)

core_samples = db.core_sample_indices_
#print "core samples", core_samples
labels = db.labels_
#print labels
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
clusters = [ResArray[labels == i] for i in xrange(n_clusters_)]
#print "Clustered locations" , clusters
#print k                
print('Estimated number of clusters: %d' % n_clusters_)
#print X


for index in range( len(clusters)):
    for j in range ( len(clusters[index])):
        for l in range( len(ResArray)):
            if (clusters[index][j][0] == ResArray[l][0]) and (clusters[index][j][1] == ResArray[l][1]):
                clusters[index][j] = songList[l]
                    
tempoList = []

for cluster in clusters:
    cantMatch = 0
    noDetails = 0
    sizeCluster = len(cluster)
    tempoList = []
    for k in range(sizeCluster):
        result = sd.getSongDetails(int(cluster[k][0]))
        if result[0] != "No song details" and result[0] != '' and result[1] != '':
            tempo = en.retrieveTempo(result[0], result[1])
            if tempo == 0:
                cantMatch += 1
            tempoList.append(tempo)
        else:
            noDetails += 1      
    tempoArray = np.array(tempoList)  
    print "Size of Cluster", sizeCluster
    print "mean",  np.mean(tempoArray, axis=0) 
    print "Std dev", np.std(tempoArray, axis=0) 
    print "No details locally", noDetails
    print "Can't match with echonest", cantMatch
    print "/n"