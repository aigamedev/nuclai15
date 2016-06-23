import os
import sys
import bootstrap     # Demonstration specific setup.
# import scipy.misc               # Image loading and manipulation.
import vispy.scene              # Canvas & visuals for rendering.
import numpy

import random
import collections
import math

from vispy.geometry import curves


class Application(object):

    SEGMENT_SIZE = 30
    MOVE_ALONG_STEP_SIZE = 15
    TOP_PATHS_NUMBER = 5
    SAMPLE_SIZE = 150
    SCALE_FACTOR = 200
    VECTOR_POINT = int(SEGMENT_SIZE / 2) # the point whre we draw vectors from, if None - we draw vectors for each point
    TELEPORT_THRESHOLD = 40 # it defines a disatnce where we elimiate a segment - we skip all teleports


    def __init__(self, example_idx, title='nucl.ai16'): #, range=(0,850)):
        self.canvas = vispy.scene.SceneCanvas(
                                title=title,
                                size=(1280, 720),
                                bgcolor='black',
                                show=False,
                                keys='interactive')

        if example_idx != 2:
            # shorten segment_size, the examples 0 and 1 display the whole segment, only the example 2 advance
            self.SEGMENT_SIZE = 10
            self.VECTOR_POINT = int(self.SEGMENT_SIZE / 2)

        self.example_idx = example_idx
        self.widget = self.canvas.central_widget
        self.view = self.canvas.central_widget.add_view()
        self.marker = vispy.scene.Markers(pos=numpy.asarray([[0,0]]), face_color='red', size=0, parent=self.view.scene)
        # prepare display
        self.lines = []
        self.vectors = []
        self.colors = []
        for i in range(self.TOP_PATHS_NUMBER):
            vectors_line = []
            color = numpy.random.rand(3)
            self.colors.append(color)
            line = vispy.scene.Line(parent=self.view.scene, color=color, width=3, connect='strip', method='agg')
            line.transform = vispy.visuals.transforms.MatrixTransform()
            self.lines.append(line)
            for j in range(self.SEGMENT_SIZE):
                if not self.VECTOR_POINT or self.VECTOR_POINT == j:
                    arr1 = vispy.scene.Arrow(numpy.asarray([[0,0],[0,0]]), parent=self.view.scene, color=color, width=2, method='agg', arrow_size=20.0)
                    arr1.transform = vispy.visuals.transforms.MatrixTransform()
                    arr2 = vispy.scene.Arrow(numpy.asarray([[0,0],[0,0]]), parent=self.view.scene, color=color, width=2, method='agg', arrow_size=20.0)
                    arr2.transform = arr1.transform
                    self.marker.transform = arr1.transform
                    vectors_line.append([arr1, arr2])
                else: vectors_line.append([None, None])
            self.vectors.append(vectors_line)


        self.timer_toggle = True
        self.selected_path = []
        self.mouse_moved = True
        self.draw_along_closets_index = 0

        # init mouse with some random value
        self.mouse_xy = ( ( numpy.random.rand(2) * 10 - 5 ) - numpy.asarray(self.canvas.size) / 2 ) * self.SCALE_FACTOR

        # read data
        self.data = {}
        self.user_team_lookup = {}

        for idx, row in enumerate(numpy.genfromtxt(os.path.join('csv', 'data.csv'), delimiter=',')):
            if idx == 0: continue
            hero_id = int(row[1])
            coordinates = numpy.array(row[2:4])
            coordinates *= self.SCALE_FACTOR
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
            # self.segments[hero_id] = numpy.asarray([self.data[hero_id][i:i+SEGMENT_SIZE] for i in range(0, len(self.data[hero_id]), SEGMENT_SIZE)])
            self.segments[hero_id] = numpy.array_split( self.data[hero_id], math.ceil(len(self.data[hero_id]) / float(self.SEGMENT_SIZE)) )
            for idx, segment in enumerate(self.segments[hero_id]):
                for idx_point, point in enumerate(segment): 
                    if idx_point == 0: continue
                    if math.hypot(point[2], point[3]) > self.TELEPORT_THRESHOLD:
                    #if math.fabs(point[0] - segment[idx_point -1][0]) > TELEPORT_THRESHOLD or math.fabs(point[1] - segment[idx_point -1][1]) > TELEPORT_THRESHOLD:
                        self.segments[hero_id][idx] = [] # skip teleports 
                        continue

        # Set 2D camera (the camera will scale to the contents in the scene)
        #self.view.camera = vispy.scene.PanZoomCamera(aspect=1)
        # flip y-axis to have correct aligment
        #self.view.camera.flip = (0, 1, 0)
        #self.view.camera.set_range(range)

        self.grid = vispy.scene.visuals.GridLines(parent=self.view.scene, color=(1, 1, 1, 1))
        self.grid.transform = vispy.visuals.transforms.MatrixTransform()
        self.grid.transform.translate(numpy.asarray(self.canvas.size) / 2)
        self.canvas.show(visible=True)
        # HACK: Bug in VisPy 0.5.0-dev requires a click for layout to occur.
        self.canvas.events.mouse_press()


        @self.canvas.events.key_press.connect
        def on_key_press(event):
            if self.timer_toggle: self.timer.stop()
            else: self.timer.start()
            self.timer_toggle = not self.timer_toggle

        @self.canvas.events.resize.connect
        def on_resize(event):
            self.grid.transform.reset()
            self.grid.transform.translate(numpy.asarray(self.canvas.size) / 2)
            # @TODO: translate paths and vectors

        @self.canvas.events.mouse_move.connect
        def on_mouse_move(event):
            self.mouse_xy = (numpy.asarray(self.view.camera.transform.imap(event.pos)) - numpy.asarray(self.canvas.size) / 2) * self.SCALE_FACTOR
            self.mouse_moved = True

        @self.canvas.events.draw.connect
        def on_draw(event):
            pass

    def get_paths(self, seed = []):
        selected_paths = []

        for i in range(self.SAMPLE_SIZE):
            hero_id = random.choice(list(self.data.keys()))
            path_idx = numpy.random.random_integers(0, (len(self.segments[hero_id])-1))
            random_path = self.segments[hero_id][path_idx]
            # ignore empty and these where player hasn't moved / @TODO: would be nice to have better heurstic to say if player moved or not
            if len(random_path) and random_path[0][0] != random_path[-1][0] and random_path[0][1] != random_path[-1][1]:
                refering_x = random_path[0][0]
                refering_y = random_path[0][1]
                investiagted_point_idx = len(random_path) 
                if self.MOVE_ALONG_STEP_SIZE < investiagted_point_idx: investiagted_point_idx = self.MOVE_ALONG_STEP_SIZE
                investiagted_point_idx -= 1
                point_distance = math.hypot(random_path[investiagted_point_idx][0] - refering_x - self.mouse_xy[0], random_path[investiagted_point_idx][1] - refering_y - self.mouse_xy[1])
                selected_paths.append([point_distance, path_idx, hero_id, numpy.asarray([refering_x, refering_y])])

        for path in seed:
            random_path = self.segments[path[2]][path[1]]
            refering_x = random_path[self.draw_along_closets_index][0] # this is new center
            refering_y = random_path[self.draw_along_closets_index][1] # this is new center

            investiagted_point_idx = len(random_path) 
            if self.MOVE_ALONG_STEP_SIZE + self.draw_along_closets_index < investiagted_point_idx: investiagted_point_idx = self.MOVE_ALONG_STEP_SIZE + self.draw_along_closets_index
            investiagted_point_idx -= 1

            point_distance = math.hypot(random_path[investiagted_point_idx][0] - refering_x - self.mouse_xy[0], random_path[investiagted_point_idx][1] - refering_y - self.mouse_xy[1])
            path[0] = point_distance
            path[3] = numpy.asarray([refering_x, refering_y])
            selected_paths.append(path)

        selected_paths.sort(key=lambda x: x[0])
        return selected_paths

    def draw_vector(self, ev):
        selected_paths = self.get_paths()
        for i in range(self.TOP_PATHS_NUMBER):
            if i >= len(selected_paths):
                # clear and skip
                self.lines[i].set_data(pos=numpy.asarray([[0,0],[0,0]]))
                for p_i, point in enumerate(selected_path):
                    if self.VECTOR_POINT and p_i != self.VECTOR_POINT: continue
                    self.vectors[i][p_i][0].set_data(pos=numpy.asarray([[0,0],[0,0]]), arrows=None)

            selected_path = self.segments[selected_paths[i][2]][selected_paths[i][1]]
            self.lines[i].set_data(pos=selected_path[:,[0,1]])
            self.lines[i].transform.reset()
            self.lines[i].transform.translate((selected_path[0][0:2] * -1))
            self.lines[i].transform.translate(numpy.asarray(self.canvas.size) / 2)

            for p_i, point in enumerate(selected_path):
                if self.VECTOR_POINT and p_i != self.VECTOR_POINT: continue

                # draw the angle
                angle = (selected_paths[i][1] * self.SEGMENT_SIZE + p_i) % 361 # the index in data vector
                v_x = math.cos(angle) * math.hypot(selected_path[p_i][2], selected_path[p_i][3])
                v_y = math.sin(angle) * math.hypot(selected_path[p_i][2], selected_path[p_i][3])
                vector = numpy.asarray([[0,0], [v_x, v_y]])

                self.vectors[i][p_i][0].set_data(pos=vector, arrows=vector.reshape(1,4))
                self.vectors[i][p_i][0].transform.reset()
                self.vectors[i][p_i][0].transform.translate((selected_path[p_i][0:2]))
                self.vectors[i][p_i][0].transform.translate((selected_path[0][0:2] * -1))
                self.vectors[i][p_i][0].transform.translate(numpy.asarray(self.canvas.size) / 2)


    def draw_closest_with_team_vectors(self, ev):
        selected_paths = self.get_paths()
        for i in range(self.TOP_PATHS_NUMBER):
            if i >= len(selected_paths):
                # clear and skip
                self.lines[i].set_data(pos=numpy.asarray([[0,0],[0,0]]))

                for p_i, point in enumerate(selected_path):
                    if self.VECTOR_POINT and p_i != self.VECTOR_POINT: continue
                    self.vectors[i][p_i][0].set_data(pos=numpy.asarray([[0,0],[0,0]]), arrows=None)
                    self.vectors[i][p_i][1].set_data(pos=numpy.asarray([[0,0],[0,0]]), arrows=None)

            selected_path = self.segments[selected_paths[i][2]][selected_paths[i][1]]
            self.lines[i].set_data(pos=selected_path[:,[0,1]])
            self.lines[i].transform.reset()
            self.lines[i].transform.translate((selected_path[0][0:2] * -1))
            self.lines[i].transform.translate(numpy.asarray(self.canvas.size) / 2)

            for p_i, point in enumerate(selected_path):
                if self.VECTOR_POINT and p_i != self.VECTOR_POINT: continue
                nearest_frined = []
                nearest_enemy = []
                # get the nearest friend / enemy to 
                for hero_id in self.data.keys():
                    if hero_id != selected_paths[i][2]: # it's not the own player
                        if hero_id in self.segments and len(self.segments[hero_id]) > selected_paths[i][1] and len(self.segments[hero_id][selected_paths[i][1]]) > 0:
                            hero_point = self.segments[hero_id][selected_paths[i][1]][p_i]
                            distance = math.hypot(hero_point[0] - point[0], hero_point[1] - point[1])
                            if self.user_team_lookup[hero_id] == self.user_team_lookup[selected_paths[i][2]]: # friend
                                if len(nearest_frined) == 0 or nearest_frined[1] > distance: nearest_frined = (hero_id, distance, hero_point[0:2])
                            else: # enemy
                                if len(nearest_enemy) == 0 or nearest_enemy[1] > distance: nearest_enemy = (hero_id, distance, hero_point[0:2])

                friend_vector = numpy.asarray([point[0:2], nearest_frined[2]]) if nearest_frined else numpy.asarray([[0,0],[0,0]])
                self.vectors[i][p_i][0].set_data(pos=friend_vector, arrows=friend_vector.reshape(1,4))
                self.vectors[i][p_i][0].transform.reset()
                self.vectors[i][p_i][0].transform.translate((selected_path[0][0:2] * -1))
                self.vectors[i][p_i][0].transform.translate(numpy.asarray(self.canvas.size) / 2)
                enemy_vector = numpy.asarray([point[0:2], nearest_enemy[2]]) if nearest_enemy else numpy.asarray([[0,0],[0,0]])
                self.vectors[i][p_i][1].set_data(pos=enemy_vector, arrows=enemy_vector.reshape(1,4))


    def draw_along_closets_segment(self, ev):
        if len(self.selected_path) == 0 or self.mouse_moved:
            self.draw_along_closets_index = 0
            selected_paths = self.get_paths()
            if len(selected_paths) > 0:
                self.selected_path = selected_paths[:self.TOP_PATHS_NUMBER]
                self.mouse_moved = False
            else: return
        else:
            # advence the best path or get a new one
            selected_paths = self.get_paths([self.selected_path[0]])
            if selected_paths[0][1] != self.selected_path[0][1] or selected_paths[0][2] != self.selected_path[0][2]:
                # new path
                self.draw_along_closets_index = 0
            self.selected_path = selected_paths[:self.TOP_PATHS_NUMBER]
        full_path_len = len(self.segments[self.selected_path[0][2]][self.selected_path[0][1]])
        if self.draw_along_closets_index > full_path_len - self.MOVE_ALONG_STEP_SIZE:
            self.mouse_moved = True
            return # end of path


        for i in range(self.TOP_PATHS_NUMBER):
            if i >= len(self.selected_path):
                # clear and skip
                self.lines[i].set_data(pos=numpy.asarray([[0,0],[0,0]]))
                continue

            current = self.segments[self.selected_path[i][2]][self.selected_path[i][1]] # hero_id, segment_idx 
            draw_to = self.MOVE_ALONG_STEP_SIZE
            if i == 0:
                draw_to += self.draw_along_closets_index

            current = current[0:draw_to] 
            path_width = 5 if i == 0 else 1
            self.lines[i].set_data(pos=current[:,[0,1]], width=path_width)
            self.lines[i].transform.reset()
            self.lines[i].transform.translate((self.selected_path[i][3] * -1))

            # to have [0,0] in the screen center
            self.lines[i].transform.translate(numpy.asarray(self.canvas.size) / 2)

            if i == 0:
                # marker_point = selected_path[self.draw_along_closets_index][2:4]
                self.marker.set_data(pos=numpy.asarray([self.selected_path[i][3]]), face_color=self.colors[i], size=15)
                self.marker.transform = self.lines[i].transform
        self.draw_along_closets_index += 1


    def process(self, _):
        return

    def run(self):
        self.timer = vispy.app.Timer(interval=1.0 / 30.0)
        print(self.example_idx)
        if self.example_idx == 0:
            self.timer.connect(self.draw_vector)
        elif self.example_idx == 1:
            self.timer.connect(self.draw_closest_with_team_vectors)
        elif self.example_idx == 2:
            self.timer.connect(self.draw_along_closets_segment)
        self.timer.start(0.033) # 30 FPS
        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')

    import argparse
    parser = argparse.ArgumentParser(description='nucl.ai16')
    parser.add_argument('-e','--example', help='Description for foo argument', default=0, type=int)
    args = parser.parse_args()
    app = Application(args.example)
    app.run()
