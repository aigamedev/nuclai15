
import numpy
import math
import random

class PathsData(object):

    def __init__(self, data_file, params, advancing = False):

        self.params = params
        self.data = {}
        self.user_team_lookup = {}
        self.advancing =  advancing
        # if advancing
        self.selected_path = []
        self.advanceIdx = 0
        self.player_position = numpy.asarray([0,0])

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


    def get_paths(self, player_position = numpy.asarray([0,0]), current_path_advanced_position = 0):

        go_to = self.mouse_xy
        selected_paths = []
        player_point = player_position * self.params.SCALE_FACTOR

        def append_path(rendom_path, path_idx, hero_id, investigated_point_idx, path_advance):
            if len(random_path) and random_path[0][0] != random_path[-1][0] and random_path[0][1] != random_path[-1][1]:
                refering_point = random_path[path_advance % self.params.SEGMENT_SIZE][0:2] # refering point is the player position in the tick
                point_distance = math.hypot(random_path[investigated_point_idx][0] - refering_point[0] + player_point[0] - go_to[0],
                                            random_path[investigated_point_idx][1] - refering_point[1] + player_point[1] - go_to[1])
                selected_paths.append([point_distance, path_idx, hero_id, refering_point, random_path])

        for i in range(self.params.SAMPLE_SIZE):
            hero_id = random.choice(list(self.data.keys()))
            path_idx = numpy.random.random_integers(0, (len(self.segments[hero_id])-1))
            random_path = self.segments[hero_id][path_idx]
            self.params.MOVE_ALONG_STEP_SIZE # we investigate the point where the drawn path ends
            append_path(random_path, path_idx, hero_id, self.params.MOVE_ALONG_STEP_SIZE, 0)

        if  not self.advancing: return selected_paths # no memory - just return from here

        if self.advancing and len(self.selected_path):
            random_path = self.segments[self.selected_path[2]][self.selected_path[1]]
            investigated_point_idx = self.params.MOVE_ALONG_STEP_SIZE + current_path_advanced_position
            if investigated_point_idx >= len(random_path):
                # get into next segment
                # check which one and if it exists
                segments_jump = (self.params.MOVE_ALONG_STEP_SIZE + current_path_advanced_position) // self.params.SEGMENT_SIZE
                if self.selected_path[1] < len(self.segments[self.selected_path[2]]) and len(self.segments[self.selected_path[2]][self.selected_path[1] + segments_jump]):
                    random_path = self.segments[self.selected_path[2]][self.selected_path[1] + segments_jump]
                    investigated_point_idx = investigated_point_idx % self.params.SEGMENT_SIZE
                else:
                    random_path = []
            append_path(random_path, self.selected_path[1], self.selected_path[2], investigated_point_idx, current_path_advanced_position)
        selected_paths.sort(key=lambda x: x[0])
        if len(self.selected_path) == 0 or selected_paths[0][1] != self.selected_path[1] or selected_paths[0][2] != self.selected_path[2]:
            # new path
            self.advanceIdx = 0
        else:
            # advance
            self.advanceIdx += 1
            self.player_position = self.player_position + self.selected_path[4][self.advanceIdx][0:2] - self.selected_path[4][self.advanceIdx-1][0:2]
        self.selected_path = selected_paths[0]
        return selected_paths













