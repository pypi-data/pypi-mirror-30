# -*- coding: utf-8 -*-

"""
cherry.api
~~~~~~~~~~~~
This module implements the cherry API.
:copyright: (c) 2018 by Windson Yang
:license: MIT License, see LICENSE for more details.
"""

from .trainer import Trainer
from .classify import Result
from .analysis import Analysis
from .infomation import Info


def classify(text, lan='Chinese', split=None):
    return Result(text=text, lan=lan, split=split)


def train(lan='Chinese', test_num=0, split=None):
    return Trainer(lan=lan, test_num=test_num, split=split)


def analysis(
        lan='Chinese', test_time=10,
        test_num=60, split=None, debug=False):
    return Analysis(
        lan=lan, test_time=test_time,
        test_num=test_num, split=split, debug=debug)


def info(lan='Chinese'):
    return Info(lan=lan)
