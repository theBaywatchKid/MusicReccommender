#!/usr/bin/env python

# Haversine formula example in Python
# Author: Wayne Dyck

import math

def haversine(p1, p2):
# convert decimal degrees to radians
lat1=p1[0]
lon1=p1[1]
lat2=p2[0]
lon2=p2[1]
lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
# haversine formula 
dlon = lon2 - lon1 
dlat = lat2 - lat1 
a = math.sin(dlat/2)2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)2
c = 2 * math.asin(math.sqrt(a)) 
km = 6372.795 * c
return km
