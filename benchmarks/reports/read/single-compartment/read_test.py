#! /usr/bin/env nix-shell
#! nix-shell --pure -i python -p python pythonPackages.numpy
from __future__ import print_function

import os
import sys

prefix = os.path.dirname(os.path.realpath(__file__))

import argparse
import brain
import numpy
import time

Report = brain.CompartmentReport

args_parser = argparse.ArgumentParser()
args_parser.add_argument("--profile", "-p", action="store_true", default=False)
args_parser.add_argument("--verify", "-v", action="store_true", default=False)
args_parser.add_argument("--detailed", "-d", action="store_true", default=False)
args_parser.add_argument("--no-cache", dest="cache", action="store_false",
                         default=True)
args_parser.add_argument("--clear-os-cache", action="store_true", default=False)

try:
    options = args_parser.parse_args(sys.argv[1:])
except Exception as e:
    print(e)
    exit(-1)

layouts = [["chunked"] + i for i in [["10", "10"], ["10", "13"], ["11", "9"], ["12", "8"], ["12", "9"], ["12", "10"], ["13", "8"], ["13", "9"]]]

if options.profile:
    import cProfile
    profiler = cProfile.Profile()
else:
    profiler = None

out_dir = prefix + "/results"

class Timer(object):
    def __enter__(self):
        self.__start = time.time()

    def __exit__(self, type, value, traceback):
        self.__finish = time.time()

    def duration(self):
        return self.__finish - self.__start
timer = Timer()

class DummyData(object):
    def __init__(self, d):
        self.shape = d.shape

def clear_os_cache():
    if options.clear_os_cache:
        os.system("echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null")

def open_report(*args):
    filename = prefix + "/data/soma_"
    filename = prefix + "/data/soma_" + "_".join(args) + ".h5"
    if options.cache:
        filename += "?cache_size=auto"
    return Report(filename)

def print_stats(timings, bytes_per_operation):
    timings = numpy.array(timings)
    print("Timing (s):", numpy.sum(timings))
    if options.detailed:
        print(" ", list(timings))
    assert(len(timings) == len(bytes_per_operation))
    total_size = numpy.sum(bytes_per_operation) / 1024.0 / 1024.0
    print("Size (MiB): ", total_size)
    print("Bandwidth (MiB/s): ", total_size / numpy.sum(timings))
    if options.detailed:
        print(" ", list(size / timings))

def compute_total_bytes(data):
    size = 4
    for i in data.shape:
        size *= i
    return size

class Progress(object):
    def __init__(self, count):
        self._total = count
        self._count = 0
        print("  0%", end='')
        sys.stdout.flush()

    def __iadd__(self, increment):
        self._count += increment
        print("\b\b\b\b%3d%%" % (self._count / float(self._total) * 100),
              end='')
        if self._count >= self._total:
            print()
        sys.stdout.flush()
        return self

numpy.random.seed(0)
all_gids = open_report("chunked", "10", "13").gids

def run_benchmark(layouts, repetitions, measure, check, out_prefix):

    reference = None
    for layout in layouts:

        timings = []
        data = []

        print("%s: " % ' '.join(layout), end='')

        shuffling = range(repetitions)
        numpy.random.seed(0)
        numpy.random.shuffle(shuffling)

        progress = Progress(repetitions)
        for i in range(0, repetitions):
            report = open_report(*layout)
            ts, frames = measure(report, shuffling[i])
            if options.verify:
                data.append(frames)
            else:
                data.append(DummyData(frames))
            timings.append(ts)
            progress += 1

        out_name = out_prefix + "_".join(layout)
        if profiler:
            profiler.dump_stats(out_name + ".profile")

        total_bytes = [compute_total_bytes(d) for d in data]
        print_stats(timings, total_bytes)

        if reference == None:
            reference = data
            open(out_prefix + "bytes", "w").write(
                " ".join([str(t) for t in total_bytes]))
        elif options.verify:
            check(reference, data, layout)

        out = open(out_name, "w")
        out.write(" ".join([str(t) for t in timings]))
        out.write("\n")


def test_traces(layouts, count=200, separation=9000, first=0, repetitions=10):

    def measure(report, iteration):
        start_index = first + separation * iteration
        gids = all_gids[start_index:start_index + count]
        clear_os_cache()
        view = report.create_view(gids)
        if profiler:
            profiler.enable()
        with timer:
            t, frames = view.load_all()
        if profiler:
            profiler.disable()
        return timer.duration(), frames

    print("full sequential %d cell traces:" % count, layouts)

    run_benchmark(layouts, repetitions, measure, None,
                  out_dir + "/%d_traces_" % count)

def test_frames(layouts, separation=80, offset=0, length=10, repetitions=20):

    def measure(report, iteration):
        start = iteration * separation + offset
        end = start + length
        clear_os_cache()
        view = report.create_view()
        if profiler:
            profiler.enable()
        with timer:
            t, frames = view.load(start, end)
        assert(frames.shape[0] == int(length * 10))
        if profiler:
            profiler.disable()
        return timer.duration(), frames

    def check(reference, data, name):
        for i, (a, b) in enumerate(zip(reference, data)):
            for i in range(a.shape[0]):
                if not all(a[i] == b[i]):
                    print(a[i], b[i])
                    start, end = time_window(i)
                    raise RuntimeError(
                        "Different frame between reference and "
                        "%s: %d in [%f, %f)" % (name, i, start, end))

    print("full sequential %d frames:" % (length * 10), layouts)
    run_benchmark(layouts, repetitions, measure, check,
                  out_dir + "/%d_frames_" % (length * 10))

test_traces(layouts, count=1, repetitions=25)
test_traces(layouts, count=10)
test_traces(layouts, first=80000, count=50)
test_traces(layouts, first=180000, count=100)
test_traces(layouts, count=250)
test_traces(layouts, first=80000, count=500)
test_traces(layouts, first=180000, count=1000)
test_traces(layouts, count=2000)
test_traces(layouts, first=80000, count=4000)
test_traces(layouts, first=180000, count=8000)
test_traces(layouts, first=180000, count=16000)

test_frames(layouts, 820, 0, 0.1, 15)
test_frames(layouts, 820, 0, 1, 10)
test_frames(layouts, 820, 5200, 10, 10)
test_frames(layouts, 820, 0, 20, 10)
test_frames(layouts, 820, 4100, 50, 5)
test_frames(layouts, 820, 8200, 100, 5)
test_frames(layouts, 820, 0, 200, 5)
test_frames(layouts, 820, 4100, 400, 5)
test_frames(layouts, 820, 8200, 800, 5)

