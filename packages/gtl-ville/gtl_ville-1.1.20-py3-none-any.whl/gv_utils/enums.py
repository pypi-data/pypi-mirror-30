#!/usr/bin/env python3

from enum import Enum, unique
from itertools import chain


@unique
class RedisData(Enum):
    CP = 'cp'
    CPS = 'cps'
    SECTION = 'section'
    SECTIONS = 'sections'
    SECTIONIDS = 'section_ids'
    ZONE = 'zone'
    EID = 'eid'
    SOURCE = 'source'
    NAME = 'name'
    GEOM = 'geom'
    ATT = 'att'
    DATA = 'data'
    DATATIMESTAMP = 'data_timestamp'
    VALIDFROM = 'valid_from'


@unique
class Metric(Enum):
    SPEED = 'Speed'
    TRAVELTIME = 'Travel time'
    RELATIVESPEED = 'Relative speed'
    CONFIDENCE = 'Confidence'
    FLOW = 'Flow'
    OCCUPANCY = 'Occupancy'
    FLUIDITY = 'Fluidity'
    DENSITY = 'Density'


@unique
class AttributeEnum(Enum):
    NAME = 'Name'
    FRC = 'Road category'
    MAXSPEED = 'Maximum speed'
    FREEFLOWSPEED = 'Free flow speed'


# Enum cannot be extended
Attribute = Enum('Attribute', [(e.name, e.value) for e in chain(Metric, AttributeEnum)])


@unique
class Source(Enum):
    TOMTOMFCD = 'TomTom FCD'
    METROPME = 'Metro PME'
    SECTIONS = 'Grenoble sections'
    ZONES = 'Grenoble zones'


@unique
class Channel(Enum):
    TOMTOMFCD = 1
    METROPME = 2
    SECTIONS = 3
    ZONES = 4
