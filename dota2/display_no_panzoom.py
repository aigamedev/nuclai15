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

SEGMENT_SIZE = 100
MOVE_ALONG_STEP_SIZE = 10
MARGIN = 2
TOP_PATHS_NUMBER = 2
SAMPLE_SIZE = 200
SCALE_FACTOR = 100
SELECTED_POINT = int(SEGMENT_SIZE / 2)
TELEPORT_THRESHOLD = 250


class Application(object):

    recipe = []

    def __init__(self, title='dota2'): #, range=(0,850)):
        self.canvas = vispy.scene.SceneCanvas(
                                title=title,
                                size=(1280, 720),
                                bgcolor='black',
                                show=False,
                                keys='interactive')

        self.widget = self.canvas.central_widget
        self.view = self.canvas.central_widget.add_view()

        # prepare display
        self.lines = []
        self.vectors = []
        for i in range(TOP_PATHS_NUMBER):
            vectors_line = []
            color = numpy.random.rand(3)
            line = vispy.scene.Line(parent=self.view.scene, color=color, width=3, connect='strip', method='agg')
            line.transform = vispy.visuals.transforms.MatrixTransform()
            self.lines.append(line)
            for j in range(SEGMENT_SIZE):
                if not SELECTED_POINT or SELECTED_POINT == j:
                    arr1 = vispy.scene.Arrow(numpy.asarray([[0,0],[0,0]]), parent=self.view.scene, color=color, width=2, method='agg', arrow_size=20.0)
                    arr1.transform = vispy.visuals.transforms.MatrixTransform()
                    arr2 = vispy.scene.Arrow(numpy.asarray([[0,0],[0,0]]), parent=self.view.scene, color=color, width=2, method='agg', arrow_size=20.0)
                    arr2.transform = arr1.transform
                    vectors_line.append([arr1, arr2])
                else: vectors_line.append([None, None])
            self.vectors.append(vectors_line)

        self.timer_toggle = True

        self.selected_path = None
        self.draw_along_closets_index = 0

        self.mouse_xy = ( ( numpy.random.rand(2) * 10 - 5 ) - numpy.asarray(self.canvas.size) / 2 ) * SCALE_FACTOR

        # read data
        self.data = {}
        self.user_team_lookup = {}

        for idx, row in enumerate(numpy.genfromtxt(os.path.join('csv', 'data.csv'), delimiter=',')):
            if idx == 0: continue
            hero_id = int(row[1])
            coordinates = numpy.array([ x * SCALE_FACTOR if idx >=2 and idx <= 8 else x for idx, x in enumerate(row)])
            if hero_id in self.data: self.data[hero_id].append(numpy.array(coordinates))
            else: self.data[hero_id] = [coordinates]
            # players 0 - 4 belong to the first team 5 - 9 to the seond one - it comes from a replay data format
            if not hero_id in self.user_team_lookup: self.user_team_lookup[hero_id] = 1 if len(self.user_team_lookup.keys()) <= 4 else 2

        # prepare smaller segments
        self.segments = {}
        for hero_id in self.data.keys():
            # self.segments[hero_id] = numpy.asarray([self.data[hero_id][i:i+SEGMENT_SIZE] for i in range(0, len(self.data[hero_id]), SEGMENT_SIZE)])
            self.segments[hero_id] = numpy.array_split( self.data[hero_id], math.ceil(len(self.data[hero_id]) / float(SEGMENT_SIZE)) )
            for idx, segment in enumerate(self.segments[hero_id]):
                for idx_point, point in enumerate(segment): 
                    if idx == 0: continue
                    if math.fabs(point[2] - segment[idx_point -1][2]) > TELEPORT_THRESHOLD or math.fabs(point[3] - segment[idx_point -1][3]) > TELEPORT_THRESHOLD:
                        self.segments[hero_id][idx] = [] # skip teleoprts 
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
            self.mouse_xy = (numpy.asarray(self.view.camera.transform.imap(event.pos)) - numpy.asarray(self.canvas.size) / 2) * SCALE_FACTOR
            self.draw_along_closets_index = 0
            self.selected_path = None

        @self.canvas.events.draw.connect
        def on_draw(event):
            pass

    def get_paths(self):
        selected_paths = []
        for i in range(SAMPLE_SIZE):
            hero_id = random.choice(self.data.keys())
            path_idx = numpy.random.random_integers(0, (len(self.segments[hero_id])-1))
            random_path = self.segments[hero_id][path_idx]
            if len(random_path):
                # the single score calculated in place where the path ends makes sense for short paths,
                # for longer paths it's better to either take the closest from given set or the aggregated sum? average?
                path_distance = None
                for point_i in range(0, len(random_path), 10):
                    point_distance = math.hypot(random_path[len(random_path) - 1 - point_i][2] - random_path[0][2] - self.mouse_xy[0], random_path[len(random_path) - 1 - point_i][3] - random_path[0][3] - self.mouse_xy[1])
                    if path_distance == None or path_distance > point_distance: path_distance = point_distance
                selected_paths.append((path_distance, path_idx, hero_id))
        selected_paths.sort(key=lambda x: x[0])
        return selected_paths

    def draw_closest_with_team_vectors(self, ev):
        selected_paths = self.get_paths()
        for i in range(TOP_PATHS_NUMBER):
            if i >= len(selected_paths):
                # clear and skip
                self.lines[i].set_data(pos=numpy.asarray([[0,0],[0,0]]))
                for p_i, point in enumerate(selected_path):
                    if SELECTED_POINT and p_i != SELECTED_POINT: continue
                    self.vectors[i][p_i][0].set_data(pos=numpy.asarray([[0,0],[0,0]]), arrows=None)
                    self.vectors[i][p_i][1].set_data(pos=numpy.asarray([[0,0],[0,0]]), arrows=None)

            selected_path = self.segments[selected_paths[i][2]][selected_paths[i][1]]
            self.lines[i].set_data(pos=selected_path[:,[2,3]])
            self.lines[i].transform.reset()
            self.lines[i].transform.translate((selected_path[0][2:4] * -1))
            self.lines[i].transform.translate(numpy.asarray(self.canvas.size) / 2)
            for p_i, point in enumerate(selected_path):
                if SELECTED_POINT and p_i != SELECTED_POINT: continue
                nearest_frined = []
                nearest_enemy = []
                # get the nearest friend / enemy to 
                for hero_id in self.data.keys():
                    if hero_id != selected_paths[i][2]: # it's not the own player
                        if hero_id in self.segments and len(self.segments[hero_id]) > selected_paths[i][1] and len(self.segments[hero_id][selected_paths[i][1]]) > 0:
                            hero_point = self.segments[hero_id][selected_paths[i][1]][p_i]
                            distance = math.hypot(hero_point[2] - point[2], hero_point[3] - point[3])
                            if self.user_team_lookup[hero_id] == self.user_team_lookup[selected_paths[i][2]]: # friend
                                if len(nearest_frined) == 0 or nearest_frined[1] > distance: nearest_frined = (hero_id, distance, hero_point[2:4])
                            else: # enemy
                                if len(nearest_enemy) == 0 or nearest_enemy[1] > distance: nearest_enemy = (hero_id, distance, hero_point[2:4])

                friend_vector = numpy.asarray([point[2:4], nearest_frined[2]]) if nearest_frined else numpy.asarray([[0,0],[0,0]])
                self.vectors[i][p_i][0].set_data(pos=friend_vector, arrows=friend_vector.reshape(1,4))
                self.vectors[i][p_i][0].transform.reset()
                self.vectors[i][p_i][0].transform.translate((selected_path[0][2:4] * -1))
                self.vectors[i][p_i][0].transform.translate(numpy.asarray(self.canvas.size) / 2)

                enemy_vector = numpy.asarray([point[2:4], nearest_enemy[2]]) if nearest_enemy else numpy.asarray([[0,0],[0,0]])
                self.vectors[i][p_i][1].set_data(pos=enemy_vector, arrows=enemy_vector.reshape(1,4))


    def draw_along_closets_segment(self, ev):
        if self.selected_path == None:
            selected_paths = self.get_paths()
            if len(selected_paths) > 0:
                self.selected_path = selected_paths[:TOP_PATHS_NUMBER]
            else: return

        for i in range(TOP_PATHS_NUMBER):
            if i >= len(self.selected_path):
                # clear and skip
                self.lines[i].set_data(pos=numpy.asarray([[0,0],[0,0]]))

            selected_path = self.segments[self.selected_path[i][2]][self.selected_path[i][1]]
            selected_path = selected_path[0:self.draw_along_closets_index+MOVE_ALONG_STEP_SIZE]
            #selected_path = selected_path[0:SEGMENT_SIZE]
            self.draw_along_closets_index += MOVE_ALONG_STEP_SIZE
            if len(selected_path) == 0: 
                self.draw_along_closets_index = 0
                return # end of path
            self.lines[i].set_data(pos=selected_path[:,[2,3]], width=5)
            self.lines[i].transform.reset()
            self.lines[i].transform.translate((self.segments[self.selected_path[i][2]][self.selected_path[i][1]][0][2:4] * -1))
            self.lines[i].transform.translate(numpy.asarray(self.canvas.size) / 2)


    def process(self, _):
        return

    def run(self):
        self.timer = vispy.app.Timer(interval=1.0 / 30.0)
        #self.timer.connect(self.draw_closest_with_team_vectors)
        self.timer.connect(self.draw_along_closets_segment)
        self.timer.start(0.5)
        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')
    
    app = Application()
    app.run()
