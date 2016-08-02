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
from sure import expect, should, should_not

from epipearl import Epipearl

epiphan_url = "http://fake.example.edu"
epiphan_user = "user"
epiphan_passwd = "passwd"

# control skipping live tests according to command line option --runlive
# requires env vars EPI_URL, EPI_USER, EPI_PASSWD, EPI_PUBLISH_TYPE
livetest = pytest.mark.skipif(
        not pytest.config.getoption( "--runlive" ),
        reason = ( "need --runlive option to run, plus env vars",
            "EPI_URL, EPI_USER, EPI_PASSWD, EPI_PUBLISH_TYPE" ) )


class TestEpipearl( object ):

    def setup( self ):
        self.c = Epipearl( epiphan_url, epiphan_user, epiphan_passwd )


    @httpretty.activate
    def test_livestream_active(self):
        channel = '1'

        httpretty.register_uri( httpretty.GET,
                '%s/admin/channel%s/get_params.cgi' % ( epiphan_url, channel
                    ), body = "publish_type = 6"
        )

        response = self.c.get_params( channel=channel, params={'publish_type':''} )
        response['publish_type'].should_not.be.different_of('6')


    @httpretty.activate
    def test_get_multi_params( self ):
        channel = 'm1'

        httpretty.register_uri( httpretty.GET,
                '%s/admin/channel%s/get_params.cgi' % ( epiphan_url, channel
                    ), body = """\
publish_type = 6
videosource = D2P280084.sdi-a:0x0/50x100;D2P280084.sdi-b:50x0/50x100
streamport = 8000
product_name = Matterhorn
vendor = Epiphan Systems Inc."""
        )

        response = self.c.get_params( channel=channel, params={
            'publish_type':'',
            'videosource':'',
            'streamport':'',
            'product_name':'',
            'vendor': '' } )

        response['publish_type'].should_not.be.different_of('6')
        response['streamport'].should_not.be.different_of('8000')
        response['product_name'].should_not.be.different_of('Matterhorn')
        response['vendor'].should_not.be.different_of('Epiphan Systems Inc.')


    @httpretty.activate
    def test_set_multi_params( self ):
        channel = 'm1'

        httpretty.register_uri( httpretty.GET,
                '%s/admin/channel%s/set_params.cgi' % ( epiphan_url, channel
                    ), body = "", status=201 )

        response = self.c.set_params( channel=channel, params={
            'publish_type':'0',
            'streamport':'8000',
            'product_name':'Matterhorn',
            'vendor': 'Epiphan Systems Inc.' } )
        assert response



    @livetest
    def test_actual_set_params( self ):
        channel = '1'
        ca_url = os.environ['EPI_URL']
        epi = Epipearl( ca_url, os.environ['EPI_USER'], os.environ['EPI_PASSWD'] )

        response = epi.set_params( channel=channel, params={ 'publish_type': os.environ['EPI_PUBLISH_TYPE'] } )
        response.should.be.ok

    @livetest
    def test_actual_get_params( self ):
        channel = '1'
        ca_url = "http://dev-epiphan002.dce.harvard.edu"
        epi = Epipearl( ca_url, os.environ['EPI_USER'], os.environ['EPI_PASSWD'] )

        response = epi.get_params( channel=channel, params={
            'publish_type':'' } )

        response['publish_type'].should_not.be.different_of( os.environ['EPI_PUBLISH_TYPE'] )

