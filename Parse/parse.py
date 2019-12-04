import sys
import re
import json

def main():
    if len(sys.argv) != 3:
        print("Usage: parse.py file_in file_out.json")
        exit(1)
    filename = sys.argv[1]
    fileout = sys.argv[2]
    with open(fileout, "w") as file:
        json.dump(parseData(filename), file, indent=4)


def parseData(filename):
    info = {}
    with open(filename, 'r') as file:
        line = file.readline()
        line = file.readline()
        line = file.readline()
        line = file.readline()
        line = line.split()
        info['start_time'] = line[3] + " " + line[4]
        line = file.readline()
        line = file.readline()
        line = file.readline()
        # Command line parameter values
        while not line.isspace():
            # print(line)
            param = re.search("^[^:]+", line)
            param = param.group().replace(" ", "_")
            param = param.lower()
            val = re.search("-?\d+\.?\d*", line)
            val = float(val.group())
            info[param] = val
            line = file.readline()
        
        line = file.readline()
        # Road info
        line = file.readline()
        vals = extract_nums(line)
        road = {
            "west_end": vals[0],
            "east_end": vals[1],
            "total": vals[2]
        }
        info['road'] = road
        # Clock info
        line = file.readline()
        vals = extract_nums(line)
        clock = {
            "start": vals[0],
            "end": vals[1],
            "tick_length": vals[2],
            "total": vals[3]
        }
        info['clock'] = clock
        # Road user sources
        line = file.readline()
        vals = extract_nums(line)
        num = int(vals[0])
        sources = []
        for i in range(num):
            source = {}
            line = file.readline()
            vals = extract_nums(line)
            line = line.split()
            # direction may have '<' in it
            source['direction'] = line[0].replace("<", "")
            source['type'] = line[1]
            source['location'] = vals[0]
            source['generating'] = vals[1]
            source['speed'] = vals[2]
            source['speed_dist'] = vals[3]
            source['length'] = vals[4]
            source['min_gap'] = vals[5]
            sources.append(source)
        info['sources'] = sources
        file.readline()
        line = file.readline()
        # Duration
        info['duration'] = extract_nums(line)[0]
        file.readline()
        # Interactions
        file.readline()
        unaggregated = extract_nums(file.readline())[0]
        recorded = extract_nums(file.readline())[0]
        file.readline()
        line = file.readline()
        interactions = []
        while not line.isspace():
            interaction = {

            }
            code = re.search("Code:(.*?)\.", line).group(1).replace(" ", "")
            extended = re.search("Extended= *(\w*) *\.", line)
            road_users = []
            extract_road_users(road_users, line)
            vals = extract_nums(line)
            line = line.split()
            interaction['id'] = vals[0]
            interaction['code'] = code
            interaction['start_time'] = vals[1]
            interaction['end_time'] = vals[2]
            interaction['start_loc'] = vals[3]
            interaction['end_loc'] = vals[4]
            interaction['extended'] = bool(extended.group(1))
            interaction['road_users'] = road_users
            interactions.append(interaction)

            line = file.readline()
        info['unaggregated'] = unaggregated
        info['recorded'] = recorded
        info['interactions'] = interactions

        # Road Users
        road_users = {}
        # "Road Users Log"
        line = file.readline() 
        # "Motor"
        line = file.readline() 
        # "Vehicles..."
        line = file.readline()
        # EastBound
        line = file.readline()
        vals = extract_nums(line)
        eastbound = {}
        eastbound['motor_vehicles'] = vals[0]
        eastbound['bicycles'] = vals[1]
        eastbound['peds'] = vals[2]
        eastbound['total'] = vals[3]
        road_users['eastbound'] = eastbound
        # WestBound
        line = file.readline()
        vals = extract_nums(line)
        westbound = {}
        westbound['motor_vehicles'] = vals[0]
        westbound['bicycles'] = vals[1]
        westbound['peds'] = vals[2]
        westbound['total'] = vals[3]
        road_users['westbound'] = westbound
        # Totals
        line = file.readline()
        vals = extract_nums(line)
        totals = {}
        totals['motor_vehicles'] = vals[0]
        totals['bicycles'] = vals[1]
        totals['peds'] = vals[2]
        totals['total'] = vals[3]
        road_users['totals'] = totals
        # Blank
        line = file.readline()
        # List
        line = file.readline()
        users = []
        while not line.isspace():
            dummy = {

            }
            vals = extract_nums(line)
            platoon = re.search("Platoon: *(\w*)", line).group(1)
            user_type = re.search("Pedestrian|Motor Vehicle|Bicycle", line).group()
            if platoon == "Yes":
                dummy['platoon'] = True
            else:
                dummy['platoon'] = False
            dummy['id'] = vals[0]
            dummy['type'] = user_type
            dummy['location'] = vals[1]
            dummy['velocity'] = vals[2]
            dummy['velocity_tick'] = vals[3]
            dummy['length'] = vals[4]
            dummy['we'] = vals[5]
            dummy['ee'] = vals[6]
            dummy['created'] = vals[7]
            dummy['removed'] = vals[8]
            users.append(dummy)
            line = file.readline()
        road_users['list'] = users
        info['road_users'] = road_users
        # Last line: Simulation finish times
        line = file.readline().split()
        info['end_time'] = line[3] + " " + line[4]
        info['prog_duration'] = float(line[9])

    return info

def extract_nums(line):
    vals = re.findall("\s?-?\d+\.?\d*\s?", line)
    vals = [float(x) for x in vals]
    return vals

def extract_road_users(road_users, line):
    users = re.findall("<Road.*?>", line)

    for user in users:
        dummy = {

        }
        vals = extract_nums(user)
        platoon = re.search("Platoon: *(\w*)", user).group(1)
        user_type = re.search("Pedestrian|Motor Vehicle|Bicycle", user).group()
        if platoon == "Yes":
            dummy['platoon'] = True
        else:
            dummy['platoon'] = False
        dummy['id'] = vals[0]
        dummy['type'] = user_type
        dummy['location'] = vals[1]
        dummy['velocity'] = vals[2]
        dummy['velocity_tick'] = vals[3]
        dummy['length'] = vals[4]
        dummy['we'] = vals[5]
        dummy['ee'] = vals[6]
        dummy['created'] = vals[7]
        dummy['removed'] = vals[8]
        road_users.append(dummy)


if __name__ == '__main__':
    main()