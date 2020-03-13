import pandas as pd
import numpy as np
from geopy import distance
import requests

def swap_tup(tuples):
    new_tup = tuples[::-1]
    return new_tup


def get_route_from_loc(source, dest):
    route_data = pd.read_csv('nyc_bike_routes_2017.csv')
    first_coords = []
    last_coords = []
    for i in range(len(route_data['the_geom'])):
        old_value = route_data['the_geom'][i]
        new_value = old_value[18:-2]
        route_data.at[i, 'the_geom'] = new_value
        all_coords = new_value.split(',')
        first_coord = all_coords[0]
        first_coords.append(first_coord)
        last_coord = all_coords[-1]
        last_coords.append(last_coord)
    route_data['first_coord'] = first_coords
    route_data['last_coord'] = last_coords
    source = swap_tup(source)
    dest = swap_tup(dest)
    loc = 1
    route = []
    while loc is not None:
        min_dist = distance.distance(dest,source).miles
        print("Source: "+str(source))
        print("Dest: "+str(dest))
        loc = None
        for i in range(len(route_data['the_geom'])):
            first_coord = swap_tup(tuple([float(i) for i in route_data['first_coord'][i].split()]))
            last_coord = swap_tup(tuple([float(i) for i in route_data['last_coord'][i].split()]))
            dist_last_dest = distance.distance(dest, last_coord).miles
            dist_first_source = distance.distance(source, first_coord).miles
            dist_score1 = dist_last_dest + dist_first_source
            dist_last_source = distance.distance(dest, first_coord).miles
            dist_first_dest = distance.distance(source, last_coord).miles
            dist_score2 = dist_last_source + dist_first_dest
            dist_score = min(dist_score1, dist_score2)
            if dist_score < min_dist and dist_first_source > 0 and dist_first_dest > 0:
                loc = i
                min_dist = dist_score
                if dist_score1 < dist_score2:
                    min_source = first_coord
                else:
                    min_source = last_coord
        if source != min_source:
            source = min_source
            route.append(source)
    return route

def create_json(route):
    arr = []
    for x in route:
        arr.append({"geometry":{"x": x[1],"y": x[0]}})
    hash = {"type": "features",
    "features": arr}
    return hash

def createApiData(source, dest):
    source = swap_tup(source)
    dest = swap_tup(dest)
    route = get_route_from_loc(source, dest)
    payload = create_json(route)
    ### needs to be sent to: https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve as a POST request
    ### tutorial for that: https://developers.arcgis.com/labs/rest/get-a-route-and-directions/
    return payload
