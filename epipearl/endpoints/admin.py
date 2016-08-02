# -*- coding: utf-8 -*-
"""http api calls to epiphan pearl."""


class Admin(object):
    """calls to admin api documented in epiphan user guide.

    epiphan pearl user guide:
    http://www.epiphan.com/userguides/pdfs/Epiphan_Pearl_userguide.pdf

    in general, methods require arguments below:
    client: epipearl client
    channel: epiphan channel call refers to
    params: dict with params to call

    methods return dict below:
    {'status_code': int http status code,
     'response_text': string with body of response}
    """

    @classmethod
    def get_params(cls, client, channel, params=None):
        if params is None:
            params = {}
        r = client.get(
                'admin/channel%s/get_params.cgi' % channel,
                params=params)
        return {
                'status_code': r.status_code,
                'response_text': r.text}

    @classmethod
    def set_params(cls, client, channel, params):
        r = client.get(
                'admin/channel%s/set_params.cgi' % channel,
                params=params)
        return {
                'status_code': r.status_code,
                'response_text': ''}


class AdminAjax(object):
    """non documented ajax calls to epiphan pearl."""

    @classmethod
    def reboot(cls, client):
        r = client.get('admin/reboot.cgi?noaction=yes')
        if r.status_code == 200 and 'Rebooting...' in r.text():
            return {'status_code': 200, 'error_msg': '', 'response': None}
        else:
            # TODO: what kind of errors can happen in this call???
            return {
                    'status_code': r.status_code,
                    'error_msg': 'error rebooting ca', 'response': r}
