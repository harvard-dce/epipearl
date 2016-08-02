#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_epipearl
----------------------------------

Tests for `epipearl` module.
"""

import os
os.environ['TESTING'] = 'True'

import json
import pytest
import httpretty
from sure import should, should_not

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
    def test_livestream_active(self):
        channel = '1'

        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/channel%s/get_params.cgi' % (epiphan_url, channel),
                body="publish_type = 6")

        response = self.c.get_params(
                channel=channel, params={'publish_type': ''})
        response['publish_type'].should_not.be.different_of('6')


    @httpretty.activate
    def test_get_multi_params(self):
        channel = 'm1'

        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/channel%s/get_params.cgi' % (
                    epiphan_url, channel),
                body="""\
publish_type = 6
videosource = D2P280084.sdi-a:0x0/50x100;D2P280084.sdi-b:50x0/50x100
streamport = 8000
product_name = Matterhorn
vendor = Epiphan Systems Inc."""
        )

        response = self.c.get_params(
                channel=channel,
                params={
                    'publish_type': '',
                    'videosource': '',
                    'streamport': '',
                    'product_name': '',
                    'vendor': ''})

        response['publish_type'].should_not.be.different_of('6')
        response['streamport'].should_not.be.different_of('8000')
        response['product_name'].should_not.be.different_of('Matterhorn')
        response['vendor'].should_not.be.different_of('Epiphan Systems Inc.')


    @httpretty.activate
    def test_set_multi_params(self):
        channel = 'm1'

        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/channel%s/set_params.cgi' % (
                    epiphan_url, channel),
                body="", status=201)

        response = self.c.set_params(
                channel=channel,
                params={
                    'publish_type': '0',
                    'streamport': '8000',
                    'product_name': 'Matterhorn',
                    'vendor': 'Epiphan Systems Inc.'})
        assert response


    @httpretty.activate
    def test_get_infocfg_ok(self):
        resp_data = resp_datafile('get_infocfg', 'ok', 'html')
        httpretty.register_uri(
                httpretty.GET,
                '%s/admin/infocfg' % epiphan_url,
                body=resp_data, status=200)

        response = self.c.get_infocfg()
        infocfg = {
                'channels': [
                    {'id': '1', 'name': 'dce_pr'},
                    {'id': '2', 'name': 'dce_live_lowbr'},
                    {'id': '3', 'name': 'dce_live'},
                    {'id': '4', 'name': 'dce_pn'}
                    ],
                'recorders': [
                    {'id': '1', 'name': 'dce_prpn'}
                    ],
                'sources': [
                    {'id': 'D2P280762.hdmi-a', 'name': 'HDMI-A'},
                    {'id': 'D2P280762.hdmi-b', 'name': 'HDMI-B'},
                    {'id': 'D2P280762.sdi-a', 'name': 'SDI-A'},
                    {'id': 'D2P280762.sdi-b', 'name': 'SDI-B'},
                    {'id': 'D2P280762.vga-a', 'name': 'VGA-A'},
                    {'id': 'D2P280762.vga-b', 'name': 'VGA-B'},
                    {'id': 'D2P280762.analog-a', 'name': 'Analog-A Audio'},
                    {'id': 'D2P280762.analog-b', 'name': 'Analog-B Audio'},
                    {'id': 'D2P280762.hdmi-a-audio', 'name': 'HDMI-A Audio'},
                    {'id': 'D2P280762.hdmi-b-audio', 'name': 'HDMI-B Audio'},
                    {'id': 'D2P280762.sdi-a-audio', 'name': 'SDI-A Audio'},
                    {'id': 'D2P280762.sdi-b-audio', 'name': 'SDI-B Audio'},
                    ]
                }
        assert response == infocfg


    @livetest
    def test_actual_set_params(self):
        channel = '1'
        ca_url = os.environ['EPI_URL']
        epi = Epipearl(
                ca_url, os.environ['EPI_USER'], os.environ['EPI_PASSWD'])

        response = epi.set_params(
                channel=channel,
                params={'publish_type': os.environ['EPI_PUBLISH_TYPE']})
        response.should.be.ok

    @livetest
    def test_actual_get_params(self):
        channel = '1'
        ca_url = os.environ['EPI_URL']
        epi = Epipearl(
                ca_url, os.environ['EPI_USER'], os.environ['EPI_PASSWD'])

        response = epi.get_params(
                channel=channel, params={'publish_type': ''})

        response['publish_type'].should_not.be.different_of(
                os.environ['EPI_PUBLISH_TYPE'])


    @livetest
    def test_live_set_channel_layout(self):
        channel_id = '1'
        layout = '{"video":[{"type":"source","position":{"left":"0%","top":"0%","width":"100%","height":"100%","keep_aspect_ratio":true},"settings":{"source":"D2P280762.sdi-b"}}],"audio":[{"type":"source","settings":{"source":"D2P280762.analog-b"}}],"background":"#000000","nosignal":{"id":"default"}}'

        ca_url = os.environ['EPI_URL']
        epi = Epipearl(
                ca_url, os.environ['EPI_USER'], os.environ['EPI_PASSWD'])

        for channel_id in ['1', '2', '3', '4']:
            response = epi.set_channel_layout(
                    channel_id=channel_id,
                    layout=layout, layout_id='1')

            assert response is not None
            r = json.loads(response)
            assert r['result']['settings'] == json.loads(layout)
