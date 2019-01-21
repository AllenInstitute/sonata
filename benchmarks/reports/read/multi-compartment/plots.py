#! /usr/bin/env nix-shell
#! nix-shell --pure -i python -p python pythonPackages.numpy pythonPackages.matplotlib

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.lines import Line2D
import os

plt.rcParams['lines.linewidth'] = 1

prefix = os.path.dirname(os.path.realpath(__file__)) + "/"

layouts = [["8", "14"], ["8", "17"], ["9", "14"]]

def make_label(layout):
    rows, cols = map(int, layout)
    def to_text(n):
        order = n // 10
        value = 2 ** (n % 10)
        return "%d%s" % (value, ["", "K", "M", "G"][order])

    return r"$%s \times %s$" % (to_text(rows), to_text(cols))

configs = [
    [["chunked"] + i for i in layouts],
    [make_label(layout) for layout in layouts]]

data_prefix = prefix + "results/"

def read_trace(*args):
    trace = np.loadtxt(data_prefix + "_".join(args))
    if trace.shape == ():
        trace = trace.reshape((1,))
    return trace

def get_total_bytes(name):
    return np.sum(np.loadtxt(data_prefix + name + "_bytes", dtype="u8"))

def get_trace_data(prefix, *keys):
    total_bytes = get_total_bytes(prefix)
    try:
        trace = read_trace(prefix, *keys)
    except IOError:
        print("Missing data for: ", keys)
        return (float("nan"), float("nan"), 0)
    return (total_bytes, np.sum(trace), len(trace))

def get_data(infix, groups):

    data = [[], None]
    for keys in configs[0]:
        bandwidths = []
        sizes = []
        for group in groups:
            total_bytes, total_time, num_ops = \
                get_trace_data("%d_" % group + infix, *keys)
            total_GiBs = total_bytes / 1024.0 / 1024.0 / 1024.0
            if num_ops == 0:
                bandwidths.append(0)
            else:
                bandwidths.append(total_GiBs / total_time)
                sizes.append(total_GiBs / num_ops)

        data[0].append(bandwidths)
        if data[1] is None:
            data[1] = sizes
        else:
            assert(data[1] == sizes)
    return data

def combined_plot():
    traces = [1, 10, 50, 100, 250, 500, 1000, 2500, 5000]
    frames = [1, 10, 100, 200, 500, 1000]

    trace_data = get_data("traces", traces)
    frame_data = get_data("frames", frames)

    fig = plt.figure(figsize=(5,3.25))
    ax = plt.subplot()

    handles = []

    for bandwidths, label in zip(frame_data[0], configs[1]):
        handles.append(
            ax.plot(frame_data[1], bandwidths, label=label, marker=".")[0])

    plt.gca().set_prop_cycle(None)
    for bandwidths in trace_data[0]:
        ax.plot(trace_data[1], bandwidths, marker=".", linestyle="--")

    handles.append(Line2D([0], [0], color="k", linestyle="-",
                          label="by frames"))
    handles.append(Line2D([0], [0], color="k", linestyle="--",
                          label="by traces"))
    ax.legend(handles=handles, loc="lower right", fontsize="small",
              title="chunk dims/access types", title_fontsize="small")

    ax.set_title("Multi-compartment read performance")
    ax.set_ylabel('Bandwidth (GiB/s)')
    ax.set_xlim(left=0, right=max(trace_data[1][-1], frame_data[1][-1]))
    ax.set_xlabel('Read operation size (GiB)')
    ax.set_ylim(bottom=0)


    plt.subplots_adjust(left=0.14, right=0.955, bottom=0.15)
    plt.savefig("multi-compartment_read.svg")

combined_plot()
