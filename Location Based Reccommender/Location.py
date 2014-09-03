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
average = 0
avgCounter = 0
for k in range(1,100):
    cur = dbse.cursor(cursorclass=MySQLdb.cursors.DictCursor)
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
    try:
        print("Silhouette Coefficient: %0.3f"
              % metrics.silhouette_score(ResArray, labels))
    except ValueError:
        print "error"   
    average += metrics.silhouette_score(ResArray, labels)
    avgCounter+=1
    
    for index in range( len(clusters)):
        for j in range ( len(clusters[index])):
            for l in range( len(ResArray)):
                if (clusters[index][j][0] == ResArray[l][0]) and (clusters[index][j][1] == ResArray[l][1]):
                    clusters[index][j] = songList[l]
                    
    #print "Songs of clustered locations ", clusters                
finalResult = float(average) / avgCounter  
print "Final average is ", finalResult   

for n in (n_clusters_):
    for k in len(n):
        print n[k]
        #en.retrieveTempo(k)
##############################################################################
# # Plot result
# import pylab as pl
# 
# unique_labels = set(labels)
# colors = pl.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
# for k, col in zip(unique_labels, colors):
#     if k == -1:
# 
#         col = 'k'
#         markersize = 6
#     class_members = [index[0] for index in np.argwhere(labels == k)]
#     cluster_core_samples = [index for index in core_samples
#                             if labels[index] == k]
#     for index in class_members:
#         x = distance_matrix[index]
#         if index in core_samples and k != -1:
#             markersize = 14
#         else:
#             markersize = 6
#         pl.plot(x[0], x[1], 'o', markerfacecolor=col,
#                 markeredgecolor='k', markersize=markersize)
# 
# pl.title('Estimated number of clusters: %d' % n_clusters_)
# pl.show()
#     