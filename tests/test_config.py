#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_config
----------------------------------

Tests for `epipearl` config module.
"""

import os
os.environ['TESTING'] = 'True'

import pytest
import requests
import httpretty

from conftest import resp_datafile
from epipearl import Epipearl
from epipearl import SettingConfigError

epiphan_url = "http://fake.example.edu"
epiphan_user = "user"
epiphan_passwd = "passwd"

# control skipping live tests according to command line option --runlive
# requires env vars EPI_URL, EPI_USER, EPI_PASSWD, EPI_PUBLISH_TYPE
livetest = pytest.mark.skipif(
        not pytest.config.getoption("--runlive"),
        reason=(
            "need --runlive option to run, plus env vars",
            "EPI_URL, EPI_USER, EPI_PASSWD, EPI_PUBLISH_TYPE"))


class TestWebUiConfig(object):

    def setup_method(self, method):
        self.c = Epipearl(epiphan_url, epiphan_user, epiphan_passwd)


    @httpretty.activate
    def test_set_ntp_ok(self):
        resp_data = resp_datafile('set_date_and_time', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/timesynccfg' % epiphan_url,
                body=resp_data)
        response = self.c.set_ntp(
                server='north-america.pool.ntp.org',
                timezone='US/Alaska')
        assert response


    @httpretty.activate
    def test_set_ntp_invalid_tz(self):
        resp_data = resp_datafile('set_date_and_time', 'invalid_tz')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/timesynccfg' % epiphan_url,
                body=resp_data)

        with pytest.raises(SettingConfigError) as e:
            self.c.set_ntp(
                    server='north-america.pool.ntp.org',
                    timezone='xuxu')
        assert 'Unsupported time zone' in e.value.message


    @httpretty.activate
    def test_set_ntp_server_did_not_take(self):
        resp_data = resp_datafile('set_date_and_time', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/timesynccfg' % epiphan_url,
                body=resp_data)

        with pytest.raises(SettingConfigError) as e:
            self.c.set_ntp(server='google.com', timezone='US/Alaska')
        assert 'expected ntp server(google.com)' in e.value.message


    @httpretty.activate
    def test_set_ntp_server_error(self):
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/timesynccfg' % epiphan_url,
                body='does not matter',
                status=501)

        with pytest.raises(requests.HTTPError) as e:
            self.c.set_ntp(server='google.com', timezone='US/Alaska')
        assert 'Server Error' in e.value.message
