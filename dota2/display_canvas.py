# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
This example demonstrates how to draw curved lines (bezier).
"""

import sys

#from vispy import app, gloo, visuals
import vispy
import vispy.app
import vispy.visuals
#import vispy.gloo
import numpy

class Canvas(vispy.app.Canvas):
    def __init__(self):
        vispy.app.Canvas.__init__(self, title='Bezier lines example',
                            keys='interactive', size=(400, 750), show=True)

        self.timer = vispy.app.Timer(connect=self.update_visuals)
        self.timer.start(0.15)

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



    def update_visuals(self, event=None):
        self.visuals = [
            vispy.visuals.LineVisual(numpy.asarray([[0,0],[numpy.random.random_integers(1, 100),100]]), color='w', width=2, method='agg'),
            vispy.visuals.LineVisual(numpy.asarray([[0,0],[10,numpy.random.random_integers(1, 100)]]), color='w', width=2, method='agg'),
        ]
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


if __name__ == '__main__':
    win = Canvas()

    if sys.flags.interactive != 1:
        vispy.app.run()
