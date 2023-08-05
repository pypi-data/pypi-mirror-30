#!/usr/bin/env python3

from enum import Enum, unique


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
class Source(Enum):
    TOMTOMFCD = 'TomTom FCD'
    METROPME = 'Metro PME'


@unique
class Channel(Enum):
    TOMTOMFCD = 'TOMTOM_FCD'
    METROPME = 'METRO_PME'
