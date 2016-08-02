# -*- coding: utf-8 -*-


import pytest


def pytest_addoption( parser ):
    parser.addoption("--runlive", action="store_true",
        help="test with live capture agents" )


