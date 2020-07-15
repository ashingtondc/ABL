import sys
import re
import json
import ast

def main():
    if len(sys.argv) != 3:
        print("Usage: parse.py file_in file_out.json")
        exit(1)
    filename = sys.argv[1]
    fileout = sys.argv[2]
    with open(fileout, "w") as file:
        json.dump(parseData(filename), file, indent=4)

def writeFile(filein, fileout):
    with open(fileout, "w") as file:
        json.dump(parseData(filein), file, indent=4)

def parseData(filename):
    info = {}
    with open(filename, 'r') as file:
        line = file.readline()
        line = file.readline()
        line = file.readline()
        line = file.readline()
        line = line.split()
        print(line)
        info['start_time'] = line[3] + " " + line[4]
        line = file.readline()
        line = file.readline()
        line = file.readline()
        # Command line parameter values
        while not line.isspace():
            print(line)
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
        # Duration of extended interactions
        line = file.readline()
        vals = extract_nums(line)
        info['interaction_time'] = float(vals[0])
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
            critical = re.search("Critical= *(\w*) *\.", line)
            critical_users = re.search("Critical Road Users= *(\[\d+, \d+\]) *\.", line)
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
            interaction['extended'] = boolean(extended.group(1))
            interaction['critical'] = boolean(critical.group(1))
            interaction['critical_users'] = ast.literal_eval(critical_users.group(1))
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
        for i in range(int(totals['total'])):
            dummy = {

            }
            vals = extract_nums(line)
            platoon = re.search("Platoon: *(\w*)", line).group(1)
            user_type = re.search("Pedestrian|Motor Vehicle|Bicycle", line).group()
            direction = re.search("EastBound|WestBound", line).group()
            left = re.search("Left On Road:\s*(\w*).", line).group(1)
            if platoon == "Yes":
                dummy['platoon'] = True
            else:
                dummy['platoon'] = False
            if left == "Yes":
                dummy['left_on_road'] = True
            else:
                dummy['left_on_road'] = False
            dummy['id'] = vals[0]
            dummy['direction'] = direction
            dummy['type'] = user_type
            dummy['create_pos'] = vals[1]
            dummy['location'] = vals[2]
            dummy['velocity'] = vals[3]
            dummy['velocity_tick'] = vals[4]
            dummy['length'] = vals[5]
            dummy['we'] = vals[6]
            dummy['ee'] = vals[7]
            dummy['created'] = vals[8]
            dummy['removed'] = vals[9]
            users.append(dummy)
            line = file.readline()
        road_users['list'] = users
        info['road_users'] = road_users
        # Interaction totals
        vals = extract_nums(line)
        info['total_interactions'] = vals[0]
        info['vru_interactions'] = vals[1]
        info['mvxmv_interactions'] = vals[2]
        # Skip redundant interaction info
        for i in range(4):
            file.readline()
        # Last line: Simulation finish times
        line = file.readline().split()
        info['end_time'] = line[3] + " " + line[4]
        info['prog_duration'] = float(line[9])

        # Calculate MVxMVxP
        # Calculate MVxMVxB
        ped = 0
        bike = 0
        for intxn in interactions:
            M = 0
            P = 0
            B = 0
            for letter in intxn['code']:
                if letter == 'M' or letter == 'm':
                    M += 1
                elif letter == 'P' or letter == 'p':
                    P += 1
                elif letter == 'B' or letter == 'b':
                    B += 1
            if M >= 2:
                if P > 0:
                    ped += 1
                elif B > 0:
                    bike += 1
        info['MV_MV_B'] = bike
        info['MV_MV_P'] = ped

    return info

def boolean(item):
    return item == "True"

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
        direction = re.search("EastBound|WestBound", line).group()
        left = re.search("Left On Road:\s*(\w*).", user).group(1)
        if platoon == "Yes":
            dummy['platoon'] = True
        else:
            dummy['platoon'] = False
        if left == "Yes":
            dummy['left_on_road'] = True
        else:
            dummy['left_on_road'] = False
        dummy['id'] = vals[0]
        dummy['direction'] = direction
        dummy['type'] = user_type
        dummy['create_pos'] = vals[1]
        dummy['location'] = vals[2]
        dummy['velocity'] = vals[3]
        dummy['velocity_tick'] = vals[4]
        dummy['length'] = vals[5]
        dummy['we'] = vals[6]
        dummy['ee'] = vals[7]
        dummy['created'] = vals[8]
        dummy['removed'] = vals[9]
        road_users.append(dummy)


if __name__ == '__main__':
    main()