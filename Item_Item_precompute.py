from scipy.sparse import lil_matrix, csr_matrix
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

numItems = 120000

#pwd = getpass()
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd= "password", # your password
                     db="soundwave", 
                     cursorclass=MySQLdb.cursors.DictCursor) 



                     
itemMatrix = lil_matrix((120000, 42000))
resultMatrix = lil_matrix((120000, 120000))

cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
curSong = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("SELECT songid, userid from actions where type = 'PLAY' order by userid ASC;")
rows = cur.fetchall()
for row in rows:
    itemMatrix[row['songid'],row['userid']] = 1 

print "Matrix set up." 

print itemMatrix.getrowview(1000)
    

    
Similarity = []
count = 0
for i in range( 1, 120000):
    currentItemMatrix = itemMatrix.getrowview(i)
    currentItemList = currentItemMatrix.rows[0]      
    for j in range(i, 120000):
        tempItemMatrix = itemMatrix.getrowview(j)
        tempItemList = tempItemMatrix.rows[0]
        for item in tempItemList:
            if item in currentItemList:
                check = True
                break
        if check == True:
            temp = cosine_similarity(currentItemMatrix, tempItemMatrix)
            resultMatrix[i,j] = temp[0][0]
            count+=1
            
        else:
            resultMatrix[i,j] = 0
        check = False    
csrMat = resultMatrix.tocsr()

print resultMatrix.getrowview(977)

np.save("ItemdataArray", csrMat.data)
np.save("ItemindArray", csrMat.indices)
np.save("ItemptrArray", csrMat.indptr)
ItemdataArray = np.load("ItemdataArray.npy")
ItemindArray =np.load("ItemindArray.npy")
ItemptrArray = np.load("ItemptrArray.npy")

new_csr = csr_matrix((ItemdataArray, ItemindArray, ItemptrArray), shape=(120000,120000))

print new_csr.getrow(977)    