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
rkp_results = song.search(artist='Laura Marling', title='Failure')
karma_police = rkp_results[0]
print 'tempo:',karma_police.audio_summary
