# appteka - helpers collection

# Copyright (C) 2018 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pyqtgraph as pg
from appteka.timestamps import get_time, get_date

class TimeStampAxisItem(pg.AxisItem):
    """ Axis with times or dates as ticks. """
    def __init__(self, what_show='time', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enableAutoSIPrefix(enable=False)
        if what_show not in ['time', 'date']:
            raise ValueError("show must be 'time' or 'date'")
        self.what_show = what_show
        
    def tickStrings(self, values, scale, spacing):
        if self.what_show == 'time':
            return [get_time(v) for v in values]
        elif self.what_show == 'date':
            return [get_date(v) for v in values]

class AxisItemsFactory:
    """ Factory for creating custom axis items with time stamps. """
    def get_items(top=True):
        res = {'bottom' : TimeStampAxisItem(what_show='time', orientation='bottom')}
        if top:
            res['top'] = TimeStampAxisItem(what_show='date', orientation='top')
        return res

class Waveform(pg.PlotWidget):
    """ Customized PyQtGraph.PlotWidget. """
    def __init__(self, xlabel=None):
        super().__init__(axisItems=AxisItemsFactory.get_items())
        self.state = {
            'online' : False,
            'plot_color' : (255,255,255),
        }
        self.showGrid(x=True, y=True)
        self.setMouseEnabled(x=True, y=False)
        self.showAxis('top')
        self.showAxis('right')
        if xlabel is not None:
            self.setLabel('bottom', xlabel)
        self.setDownsampling(mode='peak')
        self.setClipToView(True)
        self.enableAutoRange(True)
        self.curve = self.plot()

    def reset(self):
        self.clear()
        self.curve = self.plot()
        self.set_plot_color(self.state['plot_color'])
        self.setMouseEnabled(x=True, y=False)
        self.enableAutoRange(True)
        
    def set_online(self, value):
        self.state['online'] = value

    def set_plot_color(self, color):
        self.curve.setPen(color)
        self.state['plot_color'] = color

    def update_data(self, t, x):
        if self.state['online'] and not self.isVisible():
            return
        if len(t) <= 0:
            return
        self.curve.setData(t, x)
        self.setLimits(xMin=t[0], xMax=t[-1])
        self.setRange(
            xRange=(t[0], t[-1]),
            yRange=(min(x), max(x)),
            disableAutoRange=False
        )

class MultiWaveform(pg.GraphicsLayoutWidget):
    """ Customized PyQtGraph.GraphicsLayoutWidget. """
    def __init__(self):
        super().__init__()
        self.state = {
            'online' : False,
            'plot_color' : (255,255,255),
        }
        self.plots = {}
        self.curves = {}
        self._main_plot = None
        self.__main_plot_limits = None

    def get_main_plot(self):
        return self._main_plot
    def set_main_plot(self, plot):
        self._main_plot = plot
    main_plot = property(get_main_plot, set_main_plot, doc="Plot used for synchronization")

    def reset(self):
        self.curves = {}
        for key in self.plots:
            self.plots[key].clear()
            self.plots[key].enableAutoRange(True)
            self.curves[key] = self.plots[key].plot()
        self.set_plot_color(self.state['plot_color'])

    def _init_plot(self, plot):
        plot.setDownsampling(mode='peak')
        plot.showGrid(x=True, y=True)
        plot.setMouseEnabled(x=True, y=False)
        plot.showAxis('right')
        for axis in ['left', 'right']:
            plot.getAxis(axis).setStyle(tickTextWidth=40, autoExpandTextSpace=False)
        plot.enableAutoRange(True)

    def add_plot(self, key, title=None, main=False):
        self.plots[key] = self.addPlot(len(self.plots), 0, axisItems=AxisItemsFactory.get_items())
        self._init_plot(self.plots[key])
        if title is not None:
            self.plots[key].setTitle(title, justify='left')
        self.curves[key] = self.plots[key].plot()
        if main:
            self.main_plot = self.plots[key]

    def remove_plots(self):
        for key in self.plots.keys():
            self.removeItem(self.plots[key])
        self.plots = {}

    def update_data(self, key, t, x):
        if len(t) == 0:
            return
        
        xlims = (t[0], t[-1])
        
        if self.state['online']:
            if not self.isVisible():
                return
        else:
            if self.plots[key] == self.main_plot:
                self.__main_plot_limits = xlims
            elif self.main_plot is not None:
                    xlims = self.__main_plot_limits
                    
        self.curves[key].setData(t, x)
        self.plots[key].setLimits(xMin=xlims[0], xMax=xlims[-1])
        self.plots[key].setRange(xRange=xlims)
        
    def set_online(self, value):
        self.state['online'] = value
        for plot in self.plots.values():
            plot.setClipToView(value)
        
    def set_plot_color(self, color):
        for c in self.curves.values():
            c.setPen(color)
        self.state['plot_color'] = color
