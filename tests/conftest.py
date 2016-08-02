# -*- coding: utf-8 -*-

import os


cwd = os.getcwd()


def pytest_addoption(parser):
    parser.addoption(
            "--runlive", action="store_true",
            help="test with live capture agents")


def resp_datafile(config_type, error_type=None, ext='html'):
    test_data = config_type
    if error_type:
        test_data = '_'.join([config_type, error_type])

    filename = os.path.join(cwd, 'tests/resp_%s.%s' % (test_data, ext))
    data = ''
    with open(filename, 'r') as myfile:
        data = myfile.read()

    return data
