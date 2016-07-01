
import numpy
import math
import random

class PathsData(object):

    def __init__(self, data_file, params):

        self.params = params
        self.data = {}
        self.user_team_lookup = {}

        for idx, row in enumerate(numpy.genfromtxt(data_file, delimiter=',')):
            if idx == 0: continue
            hero_id = int(row[1])
            coordinates = numpy.array(row[2:4])
            coordinates *= self.params.SCALE_FACTOR
            if hero_id in self.data: self.data[hero_id].append(numpy.array(coordinates))
            else: self.data[hero_id] = [coordinates]
            # players 0 - 4 belong to the first team 5 - 9 to the seond one - it comes from a replay data format
            if not hero_id in self.user_team_lookup: self.user_team_lookup[hero_id] = 1 if len(self.user_team_lookup.keys()) <= 4 else 2 

        # append offset
        for hero_id in self.data.keys():
            for idx_point, point in enumerate(self.data[hero_id]):
                if idx_point == 0: offset = [0,0]
                else: offset = [point[0] - self.data[hero_id][idx_point-1][0], point[1] - self.data[hero_id][idx_point-1][1]]
                self.data[hero_id][idx_point] = numpy.append(point, numpy.array(offset))

        # prepare smaller segments
        self.segments = {}
        for hero_id in self.data.keys():
            self.segments[hero_id] = numpy.array_split( self.data[hero_id], math.ceil(len(self.data[hero_id]) / float(self.params.SEGMENT_SIZE)) )
            for idx, segment in enumerate(self.segments[hero_id]):
                for idx_point, point in enumerate(segment): 
                    if idx_point == 0: continue
                    if math.hypot(point[2], point[3]) > self.params.TELEPORT_THRESHOLD:
                        self.segments[hero_id][idx] = [] # skip teleports 
                        continue


    def get_paths(self, go_to, player_position = numpy.asarray([0,0]), current_path_advanced_position = 0, seed = []):

        selected_paths = []
        player_point = player_position * self.params.SCALE_FACTOR

        for i in range(self.params.SAMPLE_SIZE):
            hero_id = random.choice(list(self.data.keys()))
            path_idx = numpy.random.random_integers(0, (len(self.segments[hero_id])-1))
            random_path = self.segments[hero_id][path_idx]
            # ignore empty and these where player hasn't moved / @TODO: would be nice to have better heurstic to say if player moved or not
            if len(random_path) and random_path[0][0] != random_path[-1][0] and random_path[0][1] != random_path[-1][1]:
                refering_point = random_path[0][0:2] # the refering point is the first poin in segment - it's a possible player position. From here we count the distance.
                investiagted_point_idx = self.params.MOVE_ALONG_STEP_SIZE # we investigate the point where the drawn path ends
                point_distance = math.hypot(random_path[investiagted_point_idx][0] - refering_point[0] + player_point[0] - go_to[0], random_path[investiagted_point_idx][1] - refering_point[1] + player_point[1] - go_to[1])
                selected_paths.append([point_distance, path_idx, hero_id, refering_point])

        for path in seed:
            random_path = self.segments[path[2]][path[1]]

            investiagted_point_idx = self.params.MOVE_ALONG_STEP_SIZE + current_path_advanced_position
            if investiagted_point_idx >= len(random_path):
                # get into next segment
                # check which one and if it exists
                segments_jump = (self.params.MOVE_ALONG_STEP_SIZE + current_path_advanced_position) // self.params.SEGMENT_SIZE
                if path[1] < len(self.segments[path[2]]) and len(self.segments[path[2]][path[1] + segments_jump]):
                    random_path = self.segments[path[2]][path[1] + segments_jump]
                    investiagted_point_idx = investiagted_point_idx % self.params.SEGMENT_SIZE
                else:
                    continue # path has ended
            refering_point = random_path[current_path_advanced_position % self.params.SEGMENT_SIZE][0:2] # refering point is the player position in the tick
            point_distance = math.hypot(random_path[investiagted_point_idx][0] - refering_point[0] + player_point[0] - go_to[0], random_path[investiagted_point_idx][1] - refering_point[1] + player_point[1] - go_to[1])
            path[0] = point_distance
            path[3] = refering_point
            selected_paths.append(path)

        selected_paths.sort(key=lambda x: x[0])
        return selected_paths

