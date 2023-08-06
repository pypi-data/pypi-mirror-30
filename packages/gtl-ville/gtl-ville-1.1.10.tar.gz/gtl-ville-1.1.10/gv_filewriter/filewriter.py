#!/usr/bin/env python3

import bz2
import os

import gv_protobuf.data_pb2 as gv_pb_data
from gv_utils import datetime
from gv_utils.enums import RedisData


DATA_PATH_STRUCT = '%Y/%m/%d/%H-%M.pb.gz2'


def write_cp_data(basepath, cpdata):
    __write_pb_data(basepath, *__cp_data_to_pb(cpdata))


def write_section_data(basepath, sectiondata):
    __write_pb_data(basepath, *__section_data_to_pb(sectiondata))


def write_zone_data(basepath, zonedata):
    __write_pb_data(basepath, *__zone_data_to_pb(zonedata))


def __cp_data_to_pb(cpdata):
    cpsamples, datadate = __get_samples_date(cpdata)

    pbdata = gv_pb_data.CpData()

    for sample in cpsamples:
        pbsample = pbdata.sample.add()
        cp = sample.get(RedisData.CP.value, {})
        pbsample.cp.eid = cp.get(RedisData.EID.value)
        pbsample.cp.sourcename = cp.get(RedisData.SOURCE.value, {}).get(RedisData.NAME.value)
        pbsample.cp.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromDatetime(datadate)
    return pbdata, datadate


def __section_data_to_pb(sectiondata):
    sectionsamples, datadate = __get_samples_date(sectiondata)

    pbdata = gv_pb_data.SectionData()

    for sample in sectionsamples:
        pbsample = pbdata.sample.add()
        pbsample.section.eid = sample.get(RedisData.SECTION.value, {}).get(RedisData.EID.value)
        pbsample.section.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromDatetime(datadate)
    return pbdata, datadate


def __zone_data_to_pb(zonedata):
    zonesamples, datadate = __get_samples_date(zonedata)

    pbdata = gv_pb_data.ZoneData()

    for sample in zonesamples:
        pbsample = pbdata.sample.add()
        pbsample.section.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromDatetime(datadate)
    return pbdata, datadate


def __get_samples_date(dictdata):
    if type(dictdata) is not dict:
        return [], datetime.now(roundtominute=True)

    datadate = dictdata.get(RedisData.DATATIMESTAMP.value)
    samples = dictdata.get(RedisData.DATA.value, [])
    if type(samples) is not list:
        samples = [samples]
    return samples, datadate


def __add_sample_metrics(sample, metrics):
    for metric, value in metrics.items():
        sample.data[metric] = float(value)


def __write_pb_data(basepath, pbdata, datadate):
    __write_bytes(__get_full_path(basepath, datadate), pbdata.SerializeToString())


def __get_full_path(basepath, datadate):
    fullpath = os.path.join(basepath, datadate.strftime(DATA_PATH_STRUCT))
    directorypath = os.path.dirname(fullpath)
    if not os.path.exists(directorypath):
        os.makedirs(directorypath)
    return fullpath


def write_graph(path, graphasyaml):
    __write_bytes(path, graphasyaml)


def read_graph(path):
    return __read_bytes(path)


def __write_bytes(path, bytesdata):
    with open(path, 'wb') as file:
        file.write(bz2.compress(bytesdata))


def __read_bytes(path):
    with open(path, 'rb') as file:
        return bz2.decompress(file.read())
