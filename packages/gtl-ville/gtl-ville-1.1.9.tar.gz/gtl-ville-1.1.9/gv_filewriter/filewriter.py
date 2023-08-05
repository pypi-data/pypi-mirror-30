#!/usr/bin/env python3

import bz2
import os

import gv_protobuf.data_pb2 as gv_pb_data


DATA_PATH_STRUCT = '%Y/%m/%d/%H-%M.pb.gz2'


def write_cp_data(basepath, cpdata):
    __write_pb_data(basepath, *__cp_data_to_pb(cpdata))


def write_section_data(basepath, sectiondata):
    __write_pb_data(basepath, *__section_data_to_pb(sectiondata))


def write_zone_data(basepath, zonedata):
    __write_pb_data(basepath, *__zone_data_to_pb(zonedata))


def __cp_data_to_pb(cpdata):
    timestamp = cpdata[0].get('data_timestamp')

    pbdata = gv_pb_data.CpData()
    for sample in cpdata:
        pbsample = pbdata.sample.add()

        cp = sample.get('cp')
        pbsample.cp.eid = cp.get('eid')
        pbsample.cp.sourcename = cp.get('source').get('name')
        pbsample.cp.geom = cp.get('geom')

        for metric, value in sample.get('data').items():
            pbsample.data[metric] = float(value)
    pbdata.timestamp.FromDatetime(timestamp)

    return pbdata, timestamp


def __section_data_to_pb(sectiondata):
    timestamp = sectiondata[0].get('data_timestamp')

    pbdata = gv_pb_data.CpData()
    for sample in sectiondata:
        pbsample = pbdata.sample.add()

        section = sample.get('section')
        pbsample.section.name = section.get('name')
        pbsample.section.geom = section.get('geom')

        for metric, value in sample.get('data').items():
            pbsample.data[metric] = float(value)
    pbdata.timestamp.FromDatetime(timestamp)

    return pbdata, timestamp


def __zone_data_to_pb(zonedata):
    timestamp = zonedata[0].get('data_timestamp')

    pbdata = gv_pb_data.CpData()
    for sample in zonedata:
        pbsample = pbdata.sample.add()

        zone = sample.get('zone')
        pbsample.section.geom = zone.get('geom')

        for metric, value in sample.get('data').items():
            pbsample.data[metric] = float(value)
    pbdata.timestamp.FromDatetime(timestamp)

    return pbdata, timestamp


def __write_pb_data(basepath, timestamp, pbdata):
    with open(__get_full_path(basepath, timestamp), 'wb') as pbfile:
        pbfile.write(bz2.compress(pbdata.SerializeToString()))


def __get_full_path(basepath, timestamp):
    fullpath = os.path.join(basepath, timestamp.strftime(DATA_PATH_STRUCT))
    directorypath = os.path.dirname(fullpath)
    if not os.path.exists(directorypath):
        os.makedirs(directorypath)
    return fullpath
