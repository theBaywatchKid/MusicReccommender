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

dbse = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwaveBig", 
                     cursorclass=MySQLdb.cursors.DictCursor) 
average = 0
avgCounter = 0
for k in range(1, 1000):
    cur = dbse.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cur.execute("SELECT userid, lon, lat from actions where type = 'PLAY' and userid = %s;", k);
    
    cursorResults = cur.fetchall()
    resultList = []
    counter = 0
    for rowOrig in cursorResults:
        if rowOrig['lon'] != 0 :
            temp = rowOrig['lon'], rowOrig['lat']
            resultList.append(temp)
            counter+=1
    if counter >= 30:        
        #print resultList  
        X = StandardScaler().fit_transform(resultList)
        #print X
        db = DBSCAN(eps=0.8, min_samples=5 ).fit(X)
        core_samples = db.core_sample_indices_
        labels = db.labels_
        
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        
        clusters = [X[labels == i] for i in xrange(n_clusters_)]
        #print clusters
        
        print('Estimated number of clusters: %d' % n_clusters_)
        #print X
        print("Silhouette Coefficient: %0.3f"
              % metrics.silhouette_score(X, labels))
        print k
        average += metrics.silhouette_score(X, labels)
        avgCounter+=1

finalResult = float(average) / avgCounter  
print "Final average is ", finalResult   
##############################################################################
# # Plot result
# import pylab as pl
# 
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
#         x = X[index]
#         if index in core_samples and k != -1:
#             markersize = 14
#         else:
#             markersize = 6
#         pl.plot(x[0], x[1], 'o', markerfacecolor=col,
#                 markeredgecolor='k', markersize=markersize)
# 
# pl.title('Estimated number of clusters: %d' % n_clusters_)
# pl.show()
    