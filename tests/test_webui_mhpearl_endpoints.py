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
        self.c = Epipearl(epiphan_url, epiphan_user, epiphan_passwd)

    @httpretty.activate
    def test_set_mhpearl_settings_ok(self):
        resp_data = resp_datafile('set_mhpearl_settings', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/mhcfg' % epiphan_url,
                body=resp_data,
                status=200)

        response = WebUiMhPearl.set_mhpearl_settings(
                client=self.c,
                device_name='dev-epiphan006',
                device_channel='6',
                file_search_range_in_seconds=100,
                admin_server_url='http://52.72.59.90:80',
                admin_server_usr='jane',
                admin_server_pwd='doe',
                update_frequency_in_seconds=122,
                backup_agent=True)
        assert response
        assert httpretty.last_request().\
                parsed_body['DEVICE_USERNAME'][0] == epiphan_user
        assert httpretty.last_request().\
                parsed_body['DEVICE_PASSWORD'][0] == epiphan_passwd


    @httpretty.activate
    def test_set_mhpearl_settings_pwd_didnt_take(self):
        resp_data = resp_datafile('set_mhpearl_settings', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/mhcfg' % epiphan_url,
                body=resp_data,
                status=200)

        with pytest.raises(SettingConfigError) as e:
            response = WebUiMhPearl.set_mhpearl_settings(
                    client=self.c,
                    device_name='dev-epiphan006',
                    device_channel='6',
                    file_search_range_in_seconds=100,
                    admin_server_url='http://52.72.59.90:80',
                    admin_server_usr='jane',
                    admin_server_pwd='plumber',
                    update_frequency_in_seconds=122,
                    backup_agent=True)
        assert 'not the admin_server_passwd expected' in e.value.message
        assert httpretty.last_request().\
                parsed_body['DEVICE_USERNAME'][0] == epiphan_user
        assert httpretty.last_request().\
                parsed_body['DEVICE_PASSWORD'][0] == epiphan_passwd
        assert httpretty.last_request().\
                parsed_body['ADMIN_SERVER_PASSWD'][0] == 'plumber'


    @httpretty.activate
    def test_set_mhpearl_settings_backup_didnt_take(self):
        resp_data = resp_datafile('set_mhpearl_settings', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/mhcfg' % epiphan_url,
                body=resp_data,
                status=200)

        with pytest.raises(SettingConfigError) as e:
            response = WebUiMhPearl.set_mhpearl_settings(
                    client=self.c,
                    device_name='dev-epiphan006',
                    device_channel='6',
                    file_search_range_in_seconds=100,
                    admin_server_url='http://52.72.59.90:80',
                    admin_server_usr='jane',
                    admin_server_pwd='doe',
                    update_frequency_in_seconds=122,
                    backup_agent=False)
        assert 'backup_agent expected("ON")' in e.value.message
        assert httpretty.last_request().\
                parsed_body['DEVICE_USERNAME'][0] == epiphan_user
        assert httpretty.last_request().\
                parsed_body['DEVICE_PASSWORD'][0] == epiphan_passwd
        assert httpretty.last_request().\
                parsed_body['ADMIN_SERVER_PASSWD'][0] == 'doe'
