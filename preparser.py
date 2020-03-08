from geopy.distance import geodesic

[(-74.190534711772, 40.521762151072735), (-74.19056948467963, 40.521773306753964)]
[(-74.19060614970476, 40.521780071898384), (-74.19064375992731, 40.52178227067235), (-74.19068134634374, 40.52177984615007), (-74.19071794029497, 40.521772862077675)], -74.19075259705527 40.52176149833094, -74.19078442414441 40.52174604726635, -74.19081259901134 40.521726907387524, -74.19083639496743 40.521704573395944, -74.19083354293682 40.52165131356065, -74.19083980619706 40.52159822498065, -74.1908550775576 40.52154621016424, -74.19087909756136 40.52149615746232, -74.19091145678264 40.52144891855167, -74.1909516028827 40.5214052994183, -74.19099885353764 40.52136604142549, -74.19105240232373 40.5213318159014)

# take in [start, end] and [potential routes]

def preparse(toFrom, routes):
    distancesTo = []
    distancesFrom = []
    score = []
    steps = []
    finished = toFrom[1]
    while len(steps) == 0 or (steps[-1] != finished):
        for x in routes:
            distancesFrom.append(geodesic(toFrom[0],x))
            distancesTo.append(geodesic(toFrom[1], x))
        for x in range(len(distancesTo)-1):
            score.append(distancesTo[x].miles+distancesFrom[x].miles)
        steps.append(min(score))
        print(steps)
        toFrom[0] = steps[-1]
    return steps
