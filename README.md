This is a sample of the code created during Hack NYU 2020 by the Cruze team.

The routing algorithm works as follows:
1. NYC Open Data provides long/lat coordinates for all bike routes in the city creating a system of nodes and edges
2. pipeline() assembles the graph-like nodes and edges system into a workable JSON file (~600 MB, 18,000 datapoints)
3. A user feeds in a current location and destination - in natural language
4. A geodesic API converts the natural language into long/lat
5. A nearest-neighbor weighted routing algorithm is used to find a path between the origin and destination
6. The arcGIS API is used to find connnectors between the bike routes identified and provide turn-by-turn directions in place of the long/lat list
7. arcGIS output is parsed and cleaned up for the user

find_route.py was our first stab at the problem - it imports from the NYC Open Data API and creates a JSON string that can be sent to esri's ArcGIS routing API
preparser.py contains a nearest-neighbor pathfinding algorithm using longitude/latitude coordinates
full_api_call.py is an agglomeration and automation of the various scripts, it creates the data structure and then uses the nearest neighbor algorithm to route around the city.
