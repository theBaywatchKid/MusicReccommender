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


def getSongDetails(songid):
    dbse = MySQLdb.connect(host="localhost", # your host, usually localhost
                         user="root", # your username
                         passwd= "password", # your password
                         db="soundwaveBig", 
                         cursorclass=MySQLdb.cursors.DictCursor) 
    
    
    cur = dbse.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    
    cur.execute("SELECT artist, title from songs where songid = %s", songid)
    cursorResults = cur.fetchall()
    for rowOrig in cursorResults:

        result = rowOrig['artist'], rowOrig['title']
    return result