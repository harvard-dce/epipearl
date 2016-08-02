#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_epipearl
----------------------------------

Tests for `epipearl` module.
"""

import os
os.environ['TESTING'] = 'True'

import pytest
import requests
import httpretty

from conftest import resp_datafile
from epipearl import Epipearl

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


class TestEpipearl(object):

    def setup(self):
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
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/ajax/rename_channel.cgi' % epiphan_url,
                status=200)

        response = self.c.create_channel('channel_blah')
        assert response == '57'


    @httpretty.activate
    def test_create_channel_failed_create(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_channel.cgi' % epiphan_url,
                status=500)

        with pytest.raises(requests.HTTPError) as e:
            response = self.c.create_channel('channel_blah')
        assert '500 Server Error' in e.value.message


    @httpretty.activate
    def test_create_channel_failed_rename(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_channel.cgi' % epiphan_url,
                status=302,
                location='/admin/channel57/mediasources')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/channel57/mediasources' % epiphan_url, status=200)
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/ajax/rename_channel.cgi' % epiphan_url,
                status=500)

        with pytest.raises(requests.HTTPError) as e:
            response = self.c.create_channel('channel_blah')
        assert '500 Server Error' in e.value.message


    @httpretty.activate
    def test_set_channel_layout_ok(self):
        layout = '{"video":[{"type":"source","position":{"left":"0%","top":"0%","width":"100%","height":"100%","keep_aspect_ratio":true},"settings":{"source":"D2P280762.hdmi-b"}}],"audio":[{"type":"source","settings":{"source":"D2P280762.sdi-a"}}],"background":"#000000","nosignal":{"id":"default"}}'
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/channel57/layouts/1' % epiphan_url,
                body=layout, status=200)

        response = self.c.set_channel_layout(channel_id=57, layout=layout)
        assert response


    @httpretty.activate
    def test_set_channel_layout_error500(self):
        layout = '{"video":[{"type":"source","position":{"left":"0%","top":"0%","width":"100%","height":"100%","keep_aspect_ratio":true},"settings":{"source":"D2P280762.hdmi-b"}}],"audio":[{"type":"source","settings":{"source":"D2P280762.sdi-a"}}],"background":"#000000","nosignal":{"id":"default"}}'
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/channel57/layouts/1' % epiphan_url,
                body=layout, status=500)

        with pytest.raises(requests.HTTPError) as e:
            response = self.c.set_channel_layout(channel_id=57, layout=layout)
        assert '500 Server Error' in e.value.message


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
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/ajax/rename_channel.cgi' % epiphan_url,
                status=200)
        response = self.c.create_recorder(recorder_name='recorder_xablau')
        assert response == '57'


    @httpretty.activate
    def test_create_recorder_failed_create(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_recorder.cgi' % epiphan_url,
                status=502,
                location='/admin/recorder57/archive')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/recorder57/archive' % epiphan_url, status=500)

        with pytest.raises(requests.HTTPError) as e:
            response = self.c.create_recorder(recorder_name='recorder_xablau')
        assert '502 Server Error' in e.value.message


    @httpretty.activate
    def test_create_recorder_failed_rename(self):
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/add_recorder.cgi' % epiphan_url,
                status=302,
                location='/admin/recorder57/archive')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/recorder57/archive' % epiphan_url, status=200)
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/ajax/rename_channel.cgi' % epiphan_url,
                status=500)

        with pytest.raises(requests.HTTPError) as e:
            response = self.c.create_recorder(recorder_name='recorder_xablau')
        assert '500 Server Error' in e.value.message


    @httpretty.activate
    def test_set_recorder_channels_ok(self):
        resp_data = resp_datafile('set_recorder_channels', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/recorder57/archive' % epiphan_url,
                body=resp_data,
                status=200)
        response = self.c.set_recorder_channels(
                recorder_id='57',
                channel_list=['3', '2'])
        assert response
        assert httpretty.last_request().parsed_body['rc[]'] == ['3', '2']

    @httpretty.activate
    def test_set_recorder_channels_error500(self):
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/recorder57/archive' % epiphan_url,
                status=500)

        with pytest.raises(requests.HTTPError) as e:
            response = self.c.set_recorder_channels(
                    recorder_id='57',
                    channel_list=['3', '2'])
        assert '500 Server Error' in e.value.message


    @httpretty.activate
    def test_delete_channel_or_recorder_by_name_ok(self):
        resp_data = resp_datafile(
                'get_infocfg', 'ok', ext='html')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/infocfg' % epiphan_url,
                body=resp_data,
                status=200)
        resp_data = resp_datafile('delete_channel', 'ok')
        httpretty.register_uri(
                httpretty.POST,
                '%s/admin/channel39/status' % epiphan_url,
                body=resp_data,
                status=200)
        response = self.c.delete_channel_or_recorder_by_name('channel_blah')
        assert response is True
