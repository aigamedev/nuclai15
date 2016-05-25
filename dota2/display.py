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
        self.lines = []
        self.vectors = []
        self.timer_toggle = True
        self.mouse_xy = numpy.random.rand(2) * 10 - 5 

        # read data
        self.data = {}
        self.user_team_lookup = {}
        for idx, row in enumerate(numpy.genfromtxt(os.path.join('csv', 'data.csv'), delimiter=',')):
            if idx == 0: continue
            hero_id = int(row[1])
            #coordinates = numpy.array([row[2], row[3]])
            coordinates = numpy.array(row)
            if hero_id in self.data: self.data[hero_id].append(numpy.array(coordinates))
            else: self.data[hero_id] = [coordinates]
            if not hero_id in self.user_team_lookup: self.user_team_lookup[hero_id] = row[9]

        print(self.user_team_lookup)

        # Set 2D camera (the camera will scale to the contents in the scene)
        self.view.camera = vispy.scene.PanZoomCamera(aspect=1)
        # flip y-axis to have correct aligment
        #self.view.camera.flip = (0, 1, 0)
        #self.view.camera.set_range(range)

        self.grid = vispy.scene.visuals.GridLines(parent=self.view.scene, color=(1, 1, 1, 1))
        self.canvas.show(visible=True)
        # HACK: Bug in VisPy 0.5.0-dev requires a click for layout to occur.
        self.canvas.events.mouse_press()

        #self.draw_path(None)
        self.arrows = []
        # Implement key presses
        @self.canvas.events.key_press.connect
        def on_key_press(event):
            if self.timer_toggle: self.timer.stop()
            else: self.timer.start()
            self.timer_toggle = not self.timer_toggle


        @self.canvas.events.mouse_move.connect
        def on_mouse_move(event):
            self.mouse_xy = self.view.camera.transform.imap(event.pos)

        @self.canvas.events.draw.connect
        def on_draw(event):
            pass

    def add_vectors(self, is_init, selected_path, color, i):

        points_vectors = []
        if is_init:
            for p_i, point in enumerate(selected_path):
                if p_i == 0:
                    vector_distance = math.hypot(point[6], point[8])
                else:
                    vector_distance = math.hypot(point[2] - selected_path[p_i-1][2], point[3] - selected_path[p_i-1][3])

                vector = vispy.scene.Line(numpy.array(([0,0],[vector_distance,0])), color=color, parent=self.view.scene)
                vector_arrowhead_l = vispy.scene.Line(numpy.array(([vector_distance,0],[vector_distance - 0.0025, 0.0025])), color=color, parent=self.view.scene)
                vector_arrowhead_r = vispy.scene.Line(numpy.array(([vector_distance,0],[vector_distance - 0.0025, -0.0025])), color=color, parent=self.view.scene)

                t = vispy.visuals.transforms.MatrixTransform()

                vector.transform = t
                vector_arrowhead_l.transform = t;
                vector_arrowhead_r.transform = t;
                t.rotate(point[4],[0,0,1])
                t.translate((point[2], point[3]))

                points_vectors.append({
                    'v': vector,
                    'a_l': vector_arrowhead_l,
                    'a_r': vector_arrowhead_r
                })

            self.vectors.append(points_vectors)
        else:
            for p_i, point in enumerate(selected_path):
                if p_i == 0: vector_distance = math.hypot(point[6], point[8])
                else: vector_distance = math.hypot(point[2] - selected_path[p_i-1][2], point[3] - selected_path[p_i-1][3])

                self.vectors[i][p_i]['v'].set_data(numpy.array(([0,0],[vector_distance,0])))
                self.vectors[i][p_i]['a_l'].set_data(numpy.array(([vector_distance,0],[vector_distance - 0.0025, 0.0025])))
                self.vectors[i][p_i]['a_r'].set_data(numpy.array(([vector_distance,0],[vector_distance - 0.0025, -0.0025])))

                t = vispy.visuals.transforms.MatrixTransform()

                self.vectors[i][p_i]['v'].transform = t
                self.vectors[i][p_i]['a_l'].transform = t;
                self.vectors[i][p_i]['a_r'].transform = t;
                t.rotate(point[4],[0,0,1])
                t.translate((point[2], point[3]))


    def draw_path(self, ev):

        LINE_SIZE = 5
        MARGIN = 2
        TOP_PATHS_NUMBER = 5
        SAMPLE_SIZE = 100

        is_init = len(self.lines) == 0
        paths = []
        selected_paths = []

        for i in range(SAMPLE_SIZE):
            hero_id = random.choice(self.data.keys())
            # paths can contain each other
            # path_end = numpy.random.random_integers(LINE_SIZE, len(self.data[hero_id]))
            # paths can NOT contain each other
            path_end = numpy.random.random_integers(1, len(self.data[hero_id]) / LINE_SIZE) * LINE_SIZE
            p = numpy.asarray(self.data[hero_id][path_end - LINE_SIZE:path_end])
            selected_paths.append(([math.hypot(p[LINE_SIZE-1][2] - p[0][2] - self.mouse_xy[0], p[LINE_SIZE-1][3] - p[0][3] - self.mouse_xy[1])], p))
        
        selected_paths.sort(key=lambda x: x[0])

        for i in range(TOP_PATHS_NUMBER):

            color = numpy.random.rand(3)
            selected_path = selected_paths[i][1]

            for e_idx, _ in enumerate(selected_path):
                if e_idx != 0: 
                    selected_path[e_idx][2] -= selected_path[0][2]
                    selected_path[e_idx][3] -= selected_path[0][3]
            selected_path[0][2] -= selected_path[0][2]
            selected_path[0][3] -= selected_path[0][3]

            paths = selected_path if i == 0 else numpy.concatenate((paths, selected_path))

            if is_init:

                plot = vispy.scene.Line(pos=selected_path[:,[2,3]], parent=self.view.scene, color=color, antialias=True, method='gl')                
                self.lines.append(plot)
            else:
                self.lines[i].set_data(pos=selected_path[:,[2,3]])

            self.add_vectors(is_init, selected_path, color, i)


        if is_init:
            # center only if first
            x_min = numpy.amin(paths[:,2])
            x_max = numpy.amax(paths[:,2])
            y_min = numpy.amin(paths[:,3])
            y_max = numpy.amax(paths[:,3])
            self.view.camera.set_range((x_min - MARGIN, x_max + MARGIN), (y_min - MARGIN, y_max + MARGIN))
            is_init = False

    def process(self, _):
        return

    def run(self):
        self.timer = vispy.app.Timer(interval=1.0 / 30.0)
        self.timer.connect(self.draw_path)
        self.timer.start()
        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')
    
    app = Application()
    app.run()
