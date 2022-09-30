"""
This file demonstrates how to load in a simple set of GPS sequences, geohash them, and private match them between two parties without any unencrypted sharing or trusted third party needed.
"""

import pygeohash as pgh # We will use this to geohash the GPS sequences

all_locations = [(42.36174, -71.09059), (42.35626, -71.06457), (42.35883, -71.10182), (42.35997, -71.09216), (42.35946, -71.08817), (42.36475, -71.09190), (42.36073, -71.08752)] 
A_locations = all_locations[[0,1,2,3]]
B_locations = all_locations[[2,3,4,5,6]]


# Geohash the locations
precision = 7
A_geohashes = [pgh.encode(lat, lon, precision=precision) for lat, lon in A_locations]
B_geohashes = [pgh.encode(lat, lon, precision=precision) for lat, lon in B_locations]


# Private match the geohashes
# Using https://github.com/OpenMined/PSI/blob/master/private_set_intersection/python/
import openmined_psi as psi

def dup(do, msg, dst):
    if not do:
        return msg
    buff = msg.SerializeToString()
    dst.ParseFromString(buff)
    return dst



reveal_intersection = False
duplicate = True
c = psi.client.CreateWithNewKey(reveal_intersection)
s = psi.server.CreateWithNewKey(reveal_intersection)


fpr = 1.0 / (1000000000)
setup = dup(
    duplicate, s.CreateSetupMessage(fpr, len(A_geohashes), B_geohashes), psi.ServerSetup()
)
request = dup(duplicate, c.CreateRequest(A_geohashes), psi.Request())
resp = dup(duplicate, s.ProcessRequest(request), psi.Response())


if reveal_intersection:
    intersection = c.GetIntersection(setup, resp)
    iset = set(intersection)
    print("Intersection: {}".format(iset))
else:
    intersection = c.GetIntersectionSize(setup, resp)
    print("Intersection size: {}".format(intersection))

print("True overlap: {}".format(set(A_locations).intersection(set(B_locations))))