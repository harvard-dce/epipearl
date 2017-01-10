#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_webui_mh_pearl_endpoints
----------------------------------

Tests for `epipearl` custom matterhorn endpoints

"""

import os
os.environ['TESTING'] = 'True'

import pytest
import httpretty

from conftest import resp_datafile
from epipearl import Epipearl
from epipearl import SettingConfigError
from epipearl.endpoints.webui_mhpearl import WebUiMhPearl

epiphan_url = "http://fake.example.edu"
epiphan_user = "johnny"
epiphan_passwd = "cash"

# control skipping live tests according to command line option --runlive
# requires env vars EPI_URL, EPI_USER, EPI_PASSWD, EPI_PUBLISH_TYPE
livetest = pytest.mark.skipif(
        not pytest.config.getoption("--runlive"),
        reason=(
            "need --runlive option to run, plus env vars",
            "EPI_URL, EPI_USER, EPI_PASSWD, EPI_PUBLISH_TYPE"))


class TestMhPearl(object):

    def setup_method(self, method):
        self.resp_ok = resp_datafile('get_mhcfg', 'ok')
        self.c = Epipearl(epiphan_url, epiphan_user, epiphan_passwd)
        self.output_streams = '''{"streams": {"1920x540": "rtmp://cp123456.live.edgefcs.net/live/lab-2-presenter-delivery.stream-1920x540_1_200@121212", "960x270": "rtmp://cp123456.live.edgefcs.net/live/lab-2-presenter-delivery.stream-960x270_1_200@121212" }}'''

    @httpretty.activate
    def test_set_mhpearl_settings_ok(self):
        resp_data = resp_datafile('set_mhcfg', 'ok')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/mhcfg' % epiphan_url,
                body=self.resp_ok,
                status=200)
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/mhcfg' % epiphan_url,
                body=resp_data,
                status=200)

        response = WebUiMhPearl.set_mhpearl_settings(
                client=self.c,
                device_name='fake-ca-room',
                device_channel='6',
                device_live_channels=['5', '6'],
                output_streams=self.output_streams,
                live_nonstop=False,
                file_search_range_in_seconds=100,
                admin_server_url='http://52.72.59.90:80',
                admin_server_usr='jane',
                admin_server_pwd='doe',
                update_frequency_in_seconds=122,
                backup_agent=False)
        assert response
        assert httpretty.last_request().\
                parsed_body['DEVICE_USERNAME'][0] == epiphan_user
        assert httpretty.last_request().\
                parsed_body['DEVICE_PASSWORD'][0] == epiphan_passwd


    @httpretty.activate
    def test_set_mhpearl_settings_pwd_didnt_take(self):
        resp_data = resp_datafile('set_mhcfg', 'ok')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/mhcfg' % epiphan_url,
                body=self.resp_ok,
                status=200)
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/mhcfg' % epiphan_url,
                body=resp_data,
                status=200)

        with pytest.raises(SettingConfigError) as e:
            response = WebUiMhPearl.set_mhpearl_settings(
                    client=self.c,
                    device_name='fake-ca-room',
                    device_channel='6',
                    device_live_channels=['5', '6'],
                    output_streams=self.output_streams,
                    live_nonstop=False,
                    file_search_range_in_seconds=100,
                    admin_server_url='http://52.72.59.90:80',
                    admin_server_usr='jane',
                    admin_server_pwd='plumber',
                    update_frequency_in_seconds=122,
                    backup_agent=False)

        assert 'expected(plumber), got(doe)' in e.value.message
        assert httpretty.last_request().\
                parsed_body['DEVICE_USERNAME'][0] == epiphan_user
        assert httpretty.last_request().\
                parsed_body['DEVICE_PASSWORD'][0] == epiphan_passwd
        assert httpretty.last_request().\
                parsed_body['ADMIN_SERVER_PASSWD'][0] == 'plumber'


    @httpretty.activate
    def test_set_mhpearl_settings_backup_didnt_take(self):
        resp_data = resp_datafile('set_mhcfg', 'ok')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/mhcfg' % epiphan_url,
                body=self.resp_ok,
                status=200)
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/mhcfg' % epiphan_url,
                body=resp_data,
                status=200)

        with pytest.raises(SettingConfigError) as e:
            response = WebUiMhPearl.set_mhpearl_settings(
                    client=self.c,
                    device_name='fake-ca-room',
                    device_channel='6',
                    device_live_channels=['5', '6'],
                    output_streams=self.output_streams,
                    live_nonstop=False,
                    file_search_range_in_seconds=100,
                    admin_server_url='http://52.72.59.90:80',
                    admin_server_usr='jane',
                    admin_server_pwd='doe',
                    update_frequency_in_seconds=122,
                    backup_agent=True)

            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(response)

        assert '(BACKUP_AGENT) expected(ON)' in e.value.message
        assert httpretty.last_request().\
                parsed_body['DEVICE_USERNAME'][0] == epiphan_user
        assert httpretty.last_request().\
                parsed_body['DEVICE_PASSWORD'][0] == epiphan_passwd
        assert httpretty.last_request().\
                parsed_body['ADMIN_SERVER_PASSWD'][0] == 'doe'
