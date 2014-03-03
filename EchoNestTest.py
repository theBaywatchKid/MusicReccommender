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
from pyechonest import config
config.ECHO_NEST_API_KEY="ZQMSEM4X59VR36QVL"

from pyechonest import song


def retrieveTempo(artistName, songName):
    rkp_results = song.search(artist=artistName, title=songName)
    try:
        searchResult = rkp_results[0]
        return  searchResult.audio_summary['tempo']
    except UnboundLocalError:
        return 0
    except IndexError:        
        return 0
    
