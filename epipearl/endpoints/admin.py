# -*- coding: utf-8 -*-

import logging


class Admin( object ):

    @classmethod
    def get_params(cls, client, channel, params=None):
        if params is None:
            params = {}
        r = client.get(
                'admin/channel%s/get_params.cgi' % channel,
                params=params)
        return r

    @classmethod
    def set_params(cls, client, channel, params):
        r = client.get(
                'admin/channel%s/set_params.cgi' % channel,
                params=params)
        return r.status_code


