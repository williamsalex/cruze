import requests
import math
import json
import os


# create data - pulls data from nyc govt api

def cd():
    data = requests.get('https://data.cityofnewyork.us/api/views/cc5c-sm6z/rows.json')
    raw_data = data.json()['data']
    cleaner_data = []
    for lane in raw_data:
        coords = lane[8].split(',')
        if lane[-1] != None:
            cleaner_data.append({'first_coord': (float(coords[0][18:].split(' ')[1]), float(coords[0][18:].split(' ')[0])), 'second_coord': (float(coords[1][1:-2].split(' ')[1]), float(coords[1][1:-2].split(' ')[0])), 'type': lane[-1]})
        else:
            cleaner_data.append({'first_coord': (float(coords[0][18:].split(' ')[1]), float(coords[0][18:].split(' ')[0])), 'second_coord': (float(coords[1][1:-2].split(' ')[1]), float(coords[1][1:-2].split(' ')[0])), 'type': 'Unknown'})
    return cleaner_data

# create data structure - creates a node data structure in an array of hashes

def cds(data):
    actionable_data = []
    assembly_array = []
    count = 0
    for lane in data:
        newlane = lane
        count+=1
        for option in data:
            if quick_dist(lane['first_coord'], option['first_coord']) < 0.5 and lane['first_coord'] != option['first_coord'] and lane['second_coord'] != option['second_coord']:
                assembly_array.append({'first_coord': option['first_coord'], 'second_coord': option['second_coord'], 'type': option['type']})
        newlane['options'] = assembly_array
        assembly_array = []
        if count%100 == 0:
            print(str(int(count/len(data)*100))+'%')
        actionable_data.append(newlane)
    return actionable_data

# used to calculate distance near nyc quickly - uses locally calculated constants which would need to be changed for another location

def quick_dist(coord1, coord2):
    return math.sqrt(math.pow(12430*((coord1[1]-coord2[1])/180),2)+math.pow(24901*((coord1[0]-coord2[0])/360)*0.16133111759,2))

# runs the first two functions

def pipeline():
    data = cds(cd())
    return data

# overwrites json file with node structure

def rewrite_structure(structure):
    with open('data.json', 'w', encoding = 'utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=4)
    return 'all done!'


### above is for creating data structure (currently just stored in data.json)
### below is for calculating routes utilizing said data structure

# takes in a location and feeds it through a geocoding api and does some minor formatting

def placeToCoords(placename):
    cleanName = placename.replace(' ', '%20')
    response = requests.get(f"https://api.opencagedata.com/geocode/v1/json?q={cleanName+'%20NYC%20NY%20USA'}&key={os.environ['GEOCODE_KEY']}")
    hash = response.json()['results'][0]['geometry']
    return (hash['lat'], hash['lng'])

# finds route between start and end locations using data structure created above

def find_route(start_tup, end_tup, structure):
    entry_point = [structure[0], quick_dist(start_tup, structure[0]['first_coord'])]
    for x in structure:
        dist = quick_dist(start_tup, x['first_coord'])
        if dist < entry_point[1]:
            entry_point = [x, dist]
    route = [start_tup, entry_point[0]['first_coord'], entry_point[0]['second_coord']]
    loc = entry_point[0]
    while True:
        curr_option = {'option': end_tup, 'score': quick_dist(loc['first_coord'], end_tup)*2}
        for x in loc['options']:
            if x['first_coord'] in route:
                pass
            else:
                score = quick_dist(loc['first_coord'], x['first_coord'])+quick_dist(x['second_coord'], end_tup)
                if score < curr_option['score']:
                    curr_option['score'] = score
                    curr_option['option'] = x
        if curr_option['option'] != end_tup:
            loc = next(item for item in structure if item["first_coord"] == curr_option['option']['first_coord'])
            route.append(curr_option['option']['first_coord'])
            route.append(curr_option['option']['second_coord'])
        else:
            route.append(end_tup)
            return route

# creates json structure to feed to api 

def create_json(route):
    arr = []
    for x in route:
        arr.append({"geometry":{"x": x[1],"y": x[0]}})
    hash = {"f": "json", "token": os.environ['API_KEY'], "stops": json.dumps({"type": "features", "features": arr})}
    return hash

# adds in api-specific headers

def createApiData(source, dest, structure):
    route = find_route(source, dest, structure)
    payload = create_json(route)
    headers = {"Content-Type": "application/x-www-form-urlencoded","Connection": "keep-alive"}
    router = requests.post("https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve", headers = headers, data = payload)
    return router

# cleans and organizes data returned from api

def parseData(apiData):
    miles = apiData.json()['routes']['features'][0]['attributes']['Total_Miles']
    paths = apiData.json()['routes']['features'][0]['geometry']['paths']
    return {'distance in miles': miles, 'route': paths}

# automates process of running these functions

def findRoute(start, end, structure):
    start_tup = placeToCoords(start)
    end_tup = placeToCoords(end)
    router = createApiData(start_tup, end_tup, structure)
    return parseData(router)['route']
