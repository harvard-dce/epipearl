#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_webui_channel_endpoints
----------------------------------

Tests for `epipearl` channel ui endpoints

"""

import os
os.environ['TESTING'] = 'True'

import logging
import sys
import json
import pytest
import requests
import httpretty

from conftest import resp_datafile
from epipearl import Epipearl
from epipearl import IndiscernibleResponseFromWebUiError
from epipearl import SettingConfigError
from epipearl.endpoints.webui_channel import WebUiChannel

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


class TestChannel(object):

    def setup_method(self, method):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        self.c = Epipearl(epiphan_url, epiphan_user, epiphan_passwd)

    @httpretty.activate
    def test_create_channel_ok(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_channel.cgi' % epiphan_url,
                status=302,
                location='/admin/channel57/mediasources')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/channel57/mediasources' % epiphan_url, status=200)

        response = WebUiChannel.create_channel(client=self.c)
        assert int(response) == 57


    @httpretty.activate
    def test_create_channel_status200(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_channel.cgi' % epiphan_url,
                status=200,
                body='{"success": false}')

        with pytest.raises(IndiscernibleResponseFromWebUiError) as e:
            response = WebUiChannel.create_channel(client=self.c)
        assert 'expect response status 302, but got (200)' in e.value.message


    @httpretty.activate
    def test_create_channel_status500(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_channel.cgi' % epiphan_url, status=500)

        with pytest.raises(requests.HTTPError) as e:
            response = WebUiChannel.create_channel(client=self.c)
        assert '500 Server Error' in e.value.message


    @httpretty.activate
    def test_create_channel_status301(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_channel.cgi' % epiphan_url,
                status=301,
                location='/admin/channel57/mediasources')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/channel57/mediasources' % epiphan_url, status=200)

        with pytest.raises(IndiscernibleResponseFromWebUiError) as e:
            response = WebUiChannel.create_channel(client=self.c)
        assert 'expect response STATUS 302, but got (301)' in e.value.message


    @httpretty.activate
    def test_create_channel_missing_location(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_channel.cgi' % epiphan_url,
                status=302)
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/channel57/mediasources' % epiphan_url, status=200)

        with pytest.raises(IndiscernibleResponseFromWebUiError) as e:
            response = WebUiChannel.create_channel(client=self.c)
        assert 'location header missing' in e.value.message


    @httpretty.activate
    def test_create_channel_location_missing_id(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_channel.cgi' % epiphan_url,
                status=302,
                location='/admin/channelXX/mediasources')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/channelXX/mediasources' % epiphan_url, status=200)

        with pytest.raises(IndiscernibleResponseFromWebUiError) as e:
            response = WebUiChannel.create_channel(client=self.c)
        assert 'cannot parse channel created from location' in e.value.message


    @httpretty.activate
    def test_rename_channel_ok(self):
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/ajax/rename_channel.cgi' % epiphan_url,
                status=200)

        response = WebUiChannel.rename_channel(
                client=self.c, channel_id='5', channel_name='new channel name')
        assert response == 'new channel name'


    @httpretty.activate
    def test_rename_channel_status501(self):
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/ajax/rename_channel.cgi' % epiphan_url,
                status=501)

        with pytest.raises(requests.HTTPError) as e:
            response = WebUiChannel.rename_channel(
                    client=self.c, channel_id='5',
                    channel_name='new channel name')
        assert '501 Server Error' in e.value.message


    @httpretty.activate
    def test_set_channel_layout_ok(self):
        layout = '{"video":[{"type":"source","position":{"left":"0%","top":"0%","width":"100%","height":"100%","keep_aspect_ratio":true},"settings":{"source":"D2P280762.sdi-b"}}],"audio":[{"type":"source","settings":{"source":"D2P280762.analog-b"}}],"background":"#000000","nosignal":{"id":"default"}}'

        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/channel39/layouts/1' % epiphan_url,
                body=layout, status=200)

        response = WebUiChannel.set_channel_layout(
                client=self.c, channel_id='39',
                layout=layout)
        assert response == layout


    @httpretty.activate
    def test_set_channel_layout_status403(self):
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/channel39/layouts/1' % epiphan_url,
                status=403)

        with pytest.raises(requests.HTTPError) as e:
            response = WebUiChannel.set_channel_layout(
                    client=self.c, channel_id='39',
                    layout='{}')
        assert '403 Client Error' in e.value.message


    @httpretty.activate
    def test_set_channel_rtmp_ok(self):
        resp_data = resp_datafile('set_channel_rtmp', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/channel39/streamsetup' % epiphan_url,
                body=resp_data,
                status=200)

        response = WebUiChannel.set_channel_rtmp(
                client=self.c, channel_id='39',
                rtmp_url='http://fake-fake.akamai.com',
                rtmp_stream='dev-epiphan002-presenter-delivery.stream-1920x540_1_200@355694',
                rtmp_usr='superfakeuser',
                rtmp_pwd='superfakeuser')
        assert response


    @httpretty.activate
    def test_set_channel_rtmp_pwd_didnt_take(self):
        resp_data = resp_datafile('set_channel_rtmp', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/channel39/streamsetup' % epiphan_url,
                body=resp_data,
                status=200)

        with pytest.raises(SettingConfigError) as e:
                response = WebUiChannel.set_channel_rtmp(
                        client=self.c, channel_id='39',
                        rtmp_url='http://fake-fake.akamai.com',
                        rtmp_stream='dev-epiphan002-presenter-delivery.stream-1920x540_1_200@355694',
                        rtmp_usr='superfakeuser',
                        rtmp_pwd='ladeeda')
        assert 'not the rtmp_pwd expected' in e.value.message


    @httpretty.activate
    def test_delete_channel_ok(self):
        resp_data = resp_datafile('delete_channel', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/channel39/status' % epiphan_url,
                body=resp_data,
                status=200)

        response = WebUiChannel.delete_channel(
                client=self.c, channel_id='39')
        assert response


    @httpretty.activate
    def test_delete_channel_success_not_found(self):
        resp_data = resp_datafile('delete_channel', 'missing_success_message')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/channel39/status' % epiphan_url,
                body=resp_data,
                status=200)

        with pytest.raises(SettingConfigError) as e:
            response = WebUiChannel.delete_channel(
                    client=self.c, channel_id='39')
        assert 'successful deletion message not found' in e.value.message


    @httpretty.activate
    def test_delete_recorder_ok(self):
        resp_data = resp_datafile('delete_recorder', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/recorder39/archive' % epiphan_url,
                body=resp_data,
                status=200)

        response = WebUiChannel.delete_recorder(
                client=self.c, recorder_id='39')
        assert response
        assert httpretty.last_request().parsed_body['deleteid'][0] == 'm39'


    @httpretty.activate
    def test_delete_recorder_success_not_found(self):
        resp_data = resp_datafile('delete_recorder', 'missing_success_message')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/recorder39/archive' % epiphan_url,
                body=resp_data,
                status=200)

        with pytest.raises(SettingConfigError) as e:
            response = WebUiChannel.delete_recorder(
                    client=self.c, recorder_id='39')
        assert 'successful deletion message not found' in e.value.message


    @httpretty.activate
    def test_create_recorder_ok(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_recorder.cgi' % epiphan_url,
                status=302,
                location='/admin/recorder57/archive')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/recorder57/archive' % epiphan_url, status=200)

        response = WebUiChannel.create_recorder(client=self.c)
        assert int(response) == 57



    @httpretty.activate
    def test_create_recorder_status200(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_recorder.cgi' % epiphan_url,
                status=200,
                body='{"success":false}')

        with pytest.raises(IndiscernibleResponseFromWebUiError) as e:
            response = WebUiChannel.create_recorder(client=self.c)
        assert 'expect response status 302, but got (200)' in e.value.message


    @httpretty.activate
    def test_create_recorder_status500(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_recorder.cgi' % epiphan_url, status=500)

        with pytest.raises(requests.HTTPError) as e:
            response = WebUiChannel.create_recorder(client=self.c)
        assert '500 Server Error' in e.value.message


    @httpretty.activate
    def test_create_recorder_status301(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_recorder.cgi' % epiphan_url,
                status=301,
                location='/admin/recorder57/archive')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/recorder57/archive' % epiphan_url, status=200)

        with pytest.raises(IndiscernibleResponseFromWebUiError) as e:
            response = WebUiChannel.create_recorder(client=self.c)
        assert 'expect response STATUS 302, but got (301)' in e.value.message


    @httpretty.activate
    def test_create_recorder_missing_location(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_recorder.cgi' % epiphan_url,
                status=302)
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/recorder57/archive' % epiphan_url, status=200)

        with pytest.raises(IndiscernibleResponseFromWebUiError) as e:
            response = WebUiChannel.create_recorder(client=self.c)
        assert 'location header missing' in e.value.message


    @httpretty.activate
    def test_create_recorder_location_missing_id(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_recorder.cgi' % epiphan_url,
                status=302,
                location='/admin/recorderXX/archive')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/recorderXX/archive' % epiphan_url, status=200)

        with pytest.raises(IndiscernibleResponseFromWebUiError) as e:
            response = WebUiChannel.create_recorder(client=self.c)
        assert 'cannot parse channel created from location' in e.value.message


    @httpretty.activate
    def test_rename_recorder_ok(self):
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/ajax/rename_channel.cgi' % epiphan_url,
                status=200)

        response = WebUiChannel.rename_recorder(
                client=self.c, recorder_id='5',
                recorder_name='new RECORDER name')
        assert response == 'new RECORDER name'
        assert httpretty.last_request().parsed_body['channel'][0] == 'm5'


    @httpretty.activate
    def test_set_recorder_channels_ok(self):
        resp_data = resp_datafile('set_recorder_channels', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/recorder3/archive' % epiphan_url,
                body=resp_data,
                status=200)
        response = WebUiChannel.set_recorder_channels(
                client=self.c,
                recorder_id=3,
                channel_list=['3', '2'])
        assert response
        assert set(httpretty.last_request().parsed_body['rc[]']) == \
                set(['2', '3'])


    @livetest
    def test_live_set_recorder_channels(self):
        ca_url = os.environ['EPI_URL']
        epicli = Epipearl(
                ca_url, os.environ['EPI_USER'], os.environ['EPI_PASSWD'])

        response = WebUiChannel.set_recorder_channels(
                client=epicli,
                recorder_id=2,
                channel_list=['3', '2'])
        assert response


    @httpretty.activate
    def test_set_recorder_channels_didnt_take(self):
        resp_data = resp_datafile('set_recorder_channels', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/recorder3/archive' % epiphan_url,
                body=resp_data,
                status=200)
        with pytest.raises(SettingConfigError) as e:
            response = WebUiChannel.set_recorder_channels(
                    client=self.c,
                    recorder_id=3,
                    channel_list=['3', '4'])
        assert set(httpretty.last_request().parsed_body['rc[]']) \
                == set(['4', '3'])
        assert 'channel(4) missing for recorder(3)' in e.value.message


    @httpretty.activate
    def test_recorder_settings_ok(self):
        resp_data = resp_datafile('set_recorder_settings', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/recorder3/archive' % epiphan_url,
                body=resp_data,
                status=200)
        response = WebUiChannel.set_recorder_settings(
                client=self.c,
                recorder_id=3,
                output_format='ts')
        assert response


    @httpretty.activate
    def test_recorder_settings_didnt_take(self):
        resp_data = resp_datafile('set_recorder_settings', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/recorder3/archive' % epiphan_url,
                body=resp_data,
                status=200)
        with pytest.raises(SettingConfigError) as e:
            response = WebUiChannel.set_recorder_settings(
                    client=self.c,
                    recorder_id=3,
                    output_format='avi')
        assert 'output_format expected(avi)' in e.value.message

    @livetest
    def test_live_set_channel_layout(self):
        layout = '{"video":[{"type":"source","position":{"left":"0%","top":"0%","width":"100%","height":"100%","keep_aspect_ratio":true},"settings":{"source":"D2P280762.sdi-b"}}],"audio":[{"type":"source","settings":{"source":"D2P280762.analog-b"}}],"background":"#000000","nosignal":{"id":"default"}}'

        ca_url = os.environ['EPI_URL']
        epicli = Epipearl(
                ca_url, os.environ['EPI_USER'], os.environ['EPI_PASSWD'])
        response = WebUiChannel.set_channel_layout(
                client=epicli, channel_id='2',
                layout=layout)
        assert response is not None
        r = json.loads(response)
        assert r['result']['settings'] == json.loads(layout)
