from __future__ import print_function

from collections import OrderedDict
from time import time
from .prettytable import PrettyTable

from os.path import basename

from inspect import currentframe, getframeinfo


class Singleton(type):
    _instances = {}

    def __call__(cls, timer_name="BenchIt"):
        if timer_name not in cls._instances:
            cls._instances[timer_name] = super(Singleton, cls).__call__(timer_name)
        return cls._instances[timer_name]


class BenchIt(metaclass=Singleton):

    def __init__(self, timer_name="BenchIt"):
        self.timer_name = timer_name
        self.times = OrderedDict()

        self.times['_start'] = time()
        self.last_mark = self.times['_start']
        self.auto_increment = 1
        self.marker_code = {}

    def __call__(self, marker_name=None):
        """Call bench marker with <code>; b()

        This will log the code being run on that line.
        """
        current_frame = currentframe()
        if marker_name is None:
            last_frame = current_frame.f_back
            last_frame_info = getframeinfo(last_frame)
            marker_name = last_frame_info.code_context[0].replace("; b()", "").strip()
        self.mark(marker_name, current_frame=current_frame)

    def mark(self, marker_name=None, current_frame=None):

        if marker_name is None:
            marker_name = self.auto_increment
            self.auto_increment += 1

        if not self.times.get(marker_name):
            self.times[marker_name] = []

        time_elapsed = time() - self.last_mark
        self.last_mark = time()

        self.times[marker_name].append(time_elapsed)
        if current_frame is None:
            current_frame = currentframe()
        last_frame = current_frame.f_back
        self.marker_code[marker_name] = (
            last_frame.f_code.co_filename,
            "{}:{}".format(basename(last_frame.f_code.co_filename), last_frame.f_lineno),
            last_frame.f_code.co_name
        )

    def stop(self):
        self.times['_end'] = time()

    def display(self):
        """
        Output the benchmark results in a table
        """
        x = PrettyTable(["Marker", "Method", "Line", "Hits", "Avg Time", "Runtime", "Percent"])
        x.align["Marker"] = "l"
        x.align["Hits"] = "r"
        x.align["Avg Time"] = "r"
        x.align["Runtime"] = "r"
        x.align["Percent"] = "r"
        x.align["Method"] = "l"
        x.align["Line"] = "r"
        x.padding_width = 1
        if '_end' not in self.times:
            self.times['_end'] = time()
        total_time = self.times['_end'] - self.times['_start']
        for marker, runtimes in self.times.items():
            if type(runtimes) is not list:
                continue
            x.add_row((
                marker,
                self.marker_code[marker][2],
                self.marker_code[marker][1],
                len(runtimes),
                "{0:.5f}".format(sum(runtimes) / float(len(runtimes))),
                "{0:.5f}".format(sum(runtimes)),
                "{0:.2f}".format(sum(runtimes) / total_time * 100),
            ))
        print(self.timer_name)
        print(x)
        print("Total runtime: {0:.5f}".format(total_time))
