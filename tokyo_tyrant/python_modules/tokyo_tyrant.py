#!/usr/bin/env python
################################################################################
# Tokyo Tyrant gmond module for Ganglia
# Copyright (c) 2011 Michael T. Conigliaro <mike [at] conigliaro [dot] org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
################################################################################

import os
import time


NAME_PREFIX = 'tokyo_tyrant_'
PARAMS = {
    'stats_command' : 'ssh legacy02.example.com /srv/tokyo/bin/tcrmgr inform -st localhost'
}
METRICS = {
    'time' : 0,
    'data' : {}
}
LAST_METRICS = dict(METRICS)
METRICS_CACHE_MAX = 1


def get_metrics():
    """Return all metrics"""

    global METRICS, LAST_METRICS

    if (time.time() - METRICS['time']) > METRICS_CACHE_MAX:

        # get raw metric data
        io = os.popen(PARAMS['stats_command'])

        # convert to dict
        metrics = {}
        for line in io.readlines():
            values = line.split()
            try:
                metrics[values[0]] = float(values[1])
            except ValueError:
                metrics[values[0]] = values[1]

        # update cache
        LAST_METRICS = dict(METRICS)
        METRICS = {
            'time': time.time(),
            'data': metrics
        }

    return [METRICS, LAST_METRICS]


def get_value(name):
    """Return a value for the requested metric"""

    metrics = get_metrics()[0]

    name = name[len(NAME_PREFIX):] # remove prefix from name
    try:
        result = metrics['data'][name]
    except StandardError:
        result = 0

    return result


def get_delta(name):
    """Return change over time for the requested metric"""

    # get metrics
    [curr_metrics, last_metrics] = get_metrics()

    # get delta
    name = name[len(NAME_PREFIX):] # remove prefix from name
    try:
        delta = (curr_metrics['data'][name] - last_metrics['data'][name])/(curr_metrics['time'] - last_metrics['time'])
        if delta < 0:
            delta = 0
    except StandardError:
        delta = 0

    return delta


def metric_init(lparams):
    """Initialize metric descriptors"""

    global PARAMS

    # set parameters
    for key in lparams:
        PARAMS[key] = lparams[key]

    # define descriptors
    time_max = 60
    groups = 'tokyo tyrant'
    descriptors = [
        {
            'name': NAME_PREFIX + 'rnum',
            'call_back': get_value,
            'time_max': time_max,
            'value_type': 'uint',
            'units': 'Records',
            'slope': 'both',
            'format': '%u',
            'description': 'Record Number',
            'groups': groups
        },
        {
            'name': NAME_PREFIX + 'size',
            'call_back': get_value,
            'time_max': time_max,
            'value_type': 'double',
            'units': 'Bytes',
            'slope': 'both',
            'format': '%f',
            'description': 'File Size',
            'groups': groups
        },
        {
            'name': NAME_PREFIX + 'delay',
            'call_back': get_value,
            'time_max': time_max,
            'value_type': 'float',
            'units': 'Secs',
            'slope': 'both',
            'format': '%f',
            'description': 'Replication Delay',
            'groups': groups
        },
        {
            'name': NAME_PREFIX + 'cnt_put',
            'call_back': get_delta,
            'time_max': time_max,
            'value_type': 'float',
            'units': 'Ops/Sec',
            'slope': 'both',
            'format': '%f',
            'description': 'Put Operations',
            'groups': groups
        },
        {
            'name': NAME_PREFIX + 'cnt_out',
            'call_back': get_delta,
            'time_max': time_max,
            'value_type': 'float',
            'units': 'Ops/Sec',
            'slope': 'both',
            'format': '%f',
            'description': 'Out Operations',
            'groups': groups
        },
        {
            'name': NAME_PREFIX + 'cnt_get',
            'call_back': get_delta,
            'time_max': time_max,
            'value_type': 'float',
            'units': 'Ops/Sec',
            'slope': 'both',
            'format': '%f',
            'description': 'Get Operations',
            'groups': groups
        },
        {
            'name': NAME_PREFIX + 'cnt_put_miss',
            'call_back': get_delta,
            'time_max': time_max,
            'value_type': 'float',
            'units': 'Ops/Sec',
            'slope': 'both',
            'format': '%f',
            'description': 'Put Operations Missed',
            'groups': groups
        },
        {
            'name': NAME_PREFIX + 'cnt_out_miss',
            'call_back': get_delta,
            'time_max': time_max,
            'value_type': 'float',
            'units': 'Ops/Sec',
            'slope': 'both',
            'format': '%f',
            'description': 'Out Operations Missed',
            'groups': groups
        },
        {
            'name': NAME_PREFIX + 'cnt_get_miss',
            'call_back': get_delta,
            'time_max': time_max,
            'value_type': 'float',
            'units': 'Ops/Sec',
            'slope': 'both',
            'format': '%f',
            'description': 'Get Operations Missed',
            'groups': groups
        }
    ]

    return descriptors


def metric_cleanup():
    """Cleanup"""

    pass


# the following code is for debugging and testing
if __name__ == '__main__':
    descriptors = metric_init(PARAMS)
    while True:
        for d in descriptors:
            print (('%s = %s') % (d['name'], d['format'])) % (d['call_back'](d['name']))
        print ''
        time.sleep(1)
