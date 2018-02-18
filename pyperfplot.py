#!/usr/bin/env python2
# coding: utf-8

# Copyright © 2018 - Ștefan Talpalaru <stefantalpalaru@yahoo.com> */
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/. */

import argparse
import matplotlib
import matplotlib.pyplot as plt
import perf
#from pprint import pprint

try:
    # for mypy
    from typing import * # NOQA (for flake8)
except:
    pass

def plot_results(args):
    #  type: (argparse.Namespace) -> None

    data = []

    for fn in args.file:
        suite = perf.BenchmarkSuite.load(fn)
        suite_data = []
        for bench in suite:
            suite_data.append((bench.get_name(), bench.mean(), bench.stdev()))
        data.append(suite_data)

    # remove benchmarks absent in one or more suites
    all_names = set()
    to_remove = set()
    for suite_data in data:
        for b in suite_data:
            all_names.add(b[0])
    for suite_data in data:
        suite_names = [b[0] for b in suite_data]
        for n in all_names:
            if n not in suite_names:
                to_remove.add(n)
    for i, suite_data in enumerate(data):
        data[i] = [b for b in suite_data if b[0] not in to_remove]

    # normalise the data with respect to the first suite
    normalised_data = [[(b[0], 1, b[2] / b[1]) for b in data[0]]]
    for suite_data in data[1:]:
        normalised_suite_data = []
        for i, b in enumerate(suite_data):
            normalised_mean = b[1] / data[0][i][1]
            normalised_stddev = b[2] * normalised_mean / b[1]
            normalised_suite_data.append((b[0], normalised_mean, normalised_stddev))
        normalised_data.append(normalised_suite_data)

    # plot it
    matplotlib.rc('xtick', labelsize=8)
    matplotlib.rc('ytick', labelsize=8)
    num_benchmarks = len(normalised_data[0])
    num_suites = len(normalised_data)
    width = 1. / (num_suites + 1)
    ind = range(num_benchmarks)
    fig, ax = plt.subplots(figsize=[args.width / 100., args.height / 100.], dpi=100)
    cm = plt.get_cmap('gist_rainbow')
    ax.set_axisbelow(True)
    ax.yaxis.grid(True)
    ax.set_prop_cycle(color=[cm(1. * i / num_suites) for i in range(num_suites)])
    ax.set_ylabel(args.ylabel)
    ax.set_title(args.title)
    ax.set_xticks([i + width * (num_suites / 2. - 0.5) for i in ind])
    ax.set_xticklabels([b[0] for b in normalised_data[0]], rotation=90)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.05))
    rects = []
    for i, suite_data in enumerate(normalised_data):
        rects.append(ax.bar([j + i * width for j in ind], [b[1] for b in suite_data], width, yerr=[b[2] for b in suite_data]))
    ax.legend([r[0] for r in rects], ['.'.join(fn.split('/')[-1].split('.')[:-1]) for fn in args.file])
    plt.savefig(args.output, bbox_inches='tight')
    #plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='E.g.: ./%(prog)s file1.json file2.json [...]')
    parser.add_argument('file', type=str, nargs='+', help='.json files to plot')
    parser.add_argument('-o', '--output', default='benchmarks.png', help='defaults to benchmarks.png')
    parser.add_argument('--width', default=1800, type=int)
    parser.add_argument('--height', default=1000, type=int)
    parser.add_argument('--title', default='pyperformance benchmark comparison')
    parser.add_argument('--ylabel', default='normalised run time (lower is better)')
    args = parser.parse_args()
    plot_results(args)

