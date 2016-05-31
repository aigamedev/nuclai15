# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
This example demonstrates how to draw curved lines (bezier).
"""

import sys, os

#from vispy import app, gloo, visuals
import vispy
import vispy.app
import vispy.visuals
#import vispy.gloo
import numpy
import random
import collections
import math

class Canvas(vispy.app.Canvas):
    def __init__(self):
        vispy.app.Canvas.__init__(self, title='Bezier lines example',
                            keys='interactive', size=(400, 750))

        self.timer = vispy.app.Timer(connect=self.update_visuals)
        self.timer.start(0.15)
        self.timer_toggle = True


        self.visuals = []
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

        self.show()


    def update_visuals(self, event=None):
        LINE_SIZE = 5
        MARGIN = 2
        TOP_PATHS_NUMBER = 5
        SAMPLE_SIZE = 100

        is_init = len(self.visuals) == 0
        paths = []
        selected_paths = []

        for i in range(SAMPLE_SIZE):
            hero_id = random.choice(self.data.keys())
            # paths can contain each other
            # path_end = numpy.random.random_integers(LINE_SIZE, len(self.data[hero_id]))
            # paths can NOT contain each other
            path_end = numpy.random.random_integers(1, len(self.data[hero_id]) / LINE_SIZE) * LINE_SIZE
            p = numpy.asarray(self.data[hero_id][path_end - LINE_SIZE:path_end])
            selected_paths.append(([math.hypot(p[LINE_SIZE-1][2] - p[0][2] - self.mouse_xy[0], p[LINE_SIZE-1][3] - p[0][3] - self.mouse_xy[1])], p, path_end - LINE_SIZE))
        
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

                plot = vispy.visuals.LineVisual(pos=selected_path[:,[2,3]], color=color, antialias=True, method='gl')
                self.visuals.append(plot)
            else:
                self.visuals[i].set_data(pos=selected_path[:,[2,3]])
            #self.add_vectors(is_init, selected_path, color, i, selected_paths[i][1])


        #if is_init:
            # center only if first
            # x_min = numpy.amin(paths[:,2])
            # x_max = numpy.amax(paths[:,2])
            # y_min = numpy.amin(paths[:,3])
            # y_max = numpy.amax(paths[:,3])
            # self.view.camera.set_range((x_min - MARGIN, x_max + MARGIN), (y_min - MARGIN, y_max + MARGIN))
            # is_init = False
        self.redraw()

    def redraw(self):
        self.on_resize(None) # Bug in vispy? Somehow I need to call this before update, otherwise it's not working ...
        self.update()

    def on_draw(self, event):
        vispy.gloo.clear('black')
        vispy.gloo.set_viewport(0, 0, *self.physical_size)
        for visual in self.visuals:
            visual.draw()

    def on_resize(self, event):
        # TODO: can it be somehow automatical ?
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for visual in self.visuals:
            visual.transforms.configure(canvas=self, viewport=vp)

    def on_key_press(self, event):
        if self.timer_toggle: self.timer.stop()
        else: self.timer.start()
        self.timer_toggle = not self.timer_toggle

    def on_mouse_move(self, event):
        print(event.pos)
        self.mouse_xy = event.pos



if __name__ == '__main__':
    win = Canvas()

    if sys.flags.interactive != 1:
        vispy.app.run()
