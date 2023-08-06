#!/usr/bin/env python3

import asyncio
import bz2
import functools
import os

import aiofiles
import gv_protobuf.data_pb2 as gv_pb_data
from gv_utils import datetime
from gv_utils.enums import RedisData


DATA_PATH_STRUCT = '%Y/%m/%d/%H-%M.pb.gz2'


def write_cp_data(basepath, cpdata):
    try:
        runasync = asyncio.get_event_loop().is_running()
    except RuntimeError:
        runasync = False

    if runasync:
        asyncio.ensure_future(__async_write_cp_data(basepath, cpdata))
    else:
        __write_pb_data(basepath, *__cp_data_to_pb(cpdata))


def write_section_data(basepath, sectiondata):
    try:
        runasync = asyncio.get_event_loop().is_running()
    except RuntimeError:
        runasync = False

    if runasync:
        asyncio.ensure_future(__async_write_section_data(basepath, sectiondata))
    else:
        __write_pb_data(basepath, *__section_data_to_pb(sectiondata))


def write_zone_data(basepath, zonedata):
    try:
        runasync = asyncio.get_event_loop().is_running()
    except RuntimeError:
        runasync = False

    if runasync:
        asyncio.ensure_future(__async_write_zone_data(basepath, zonedata))
    else:
        __write_pb_data(basepath, *__zone_data_to_pb(zonedata))


async def __async_write_cp_data(basepath, cpdata):
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__cp_data_to_pb, cpdata))
    __write_pb_data(basepath, pbdata, datatimestamp)


async def __async_write_section_data(basepath, sectiondata):
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__section_data_to_pb, sectiondata))
    __write_pb_data(basepath, pbdata, datatimestamp)


async def __async_write_zone_data(basepath, zonedata):
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__zone_data_to_pb, zonedata))
    __write_pb_data(basepath, pbdata, datatimestamp)


def __cp_data_to_pb(cpdata):
    cpsamples, datatimestamp = __get_samples_timestamp(cpdata)

    pbdata = gv_pb_data.CpData()

    for sample in cpsamples:
        pbsample = pbdata.sample.add()
        cp = sample.get(RedisData.CP.value, {})
        pbsample.cp.eid = cp.get(RedisData.EID.value)
        pbsample.cp.sourcename = cp.get(RedisData.SOURCE.value, {}).get(RedisData.NAME.value)
        pbsample.cp.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __section_data_to_pb(sectiondata):
    sectionsamples, datatimestamp = __get_samples_timestamp(sectiondata)

    pbdata = gv_pb_data.SectionData()

    for sample in sectionsamples:
        pbsample = pbdata.sample.add()
        pbsample.section.eid = sample.get(RedisData.SECTION.value, {}).get(RedisData.EID.value)
        pbsample.section.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __zone_data_to_pb(zonedata):
    zonesamples, datatimestamp = __get_samples_timestamp(zonedata)

    pbdata = gv_pb_data.ZoneData()

    for sample in zonesamples:
        pbsample = pbdata.sample.add()
        pbsample.section.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __get_samples_timestamp(dictdata):
    if type(dictdata) is not dict:
        return [], datetime.now(roundtominute=True).timestamp()

    datatimestamp = dictdata.get(RedisData.DATATIMESTAMP.value)
    samples = dictdata.get(RedisData.DATA.value, [])
    if type(samples) is not list:
        samples = [samples]
    return samples, int(datatimestamp)


def __add_sample_metrics(sample, metrics):
    for metric, value in metrics.items():
        sample.data[metric] = float(value)


async def __async_write_pb_data(basepath, pbdata, datatimestamp):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, pbdata.SerializeToString)
    __write_bytes(__get_full_path(basepath, datatimestamp), data)


def __write_pb_data(basepath, pbdata, datatimestamp):
    __write_bytes(__get_full_path(basepath, datatimestamp), pbdata.SerializeToString())


def __get_full_path(basepath, datatimestamp):
    fullpath = os.path.join(basepath,
                            datetime.from_timestamp(datatimestamp, roundtominute=True).strftime(DATA_PATH_STRUCT))
    directorypath = os.path.dirname(fullpath)
    if not os.path.exists(directorypath):
        os.makedirs(directorypath)
    return fullpath


def write_graph(path, graphasyaml):
    __write_bytes(path, graphasyaml)


def read_graph(path):
    return __read_bytes(path)


def __write_bytes(path, bytesdata):
    try:
        runasync = asyncio.get_event_loop().is_running()
    except RuntimeError:
        runasync = False

    if runasync:
        asyncio.ensure_future(__async_write_bytes(path, bytesdata))
    else:
        __seq_write_bytes(path, bytesdata)


async def __async_write_bytes(path, bytesdata):
    async with aiofiles.open(path, 'wb') as file:
        loop = asyncio.get_event_loop()
        compressdata = await loop.run_in_executor(None, functools.partial(bz2.compress, bytesdata))
        asyncio.ensure_future(file.write(compressdata))


def __seq_write_bytes(path, bytesdata):
    with open(path, 'wb') as file:
        file.write(bz2.compress(bytesdata))


def __read_bytes(path):
    try:
        runasync = asyncio.get_event_loop().is_running()
    except RuntimeError:
        runasync = False

    if runasync:
        return __async_read_bytes(path)
    else:
        return __seq_read_bytes(path)


async def __async_read_bytes(path):
    async with aiofiles.open(path, 'rb') as file:
        loop = asyncio.get_event_loop()
        compressdata = await file.read()
        return await loop.run_in_executor(None, functools.partial(bz2.decompress, compressdata))


def __seq_read_bytes(path):
    with open(path, 'rb') as file:
        return bz2.decompress(file.read())
