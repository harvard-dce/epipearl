# -*- coding: utf-8 -*-
"""http api and web ui calls to epiphan pearl."""

from epipearl.endpoints.webui_config import WebUiConfig


class WebUiMhPearl(object):
    """calls to dce mh_pearl custom api.

    these are custom api calls for mh_pearl. epiphan pearl firmware
    _does not_ support them out-of-the-box

    methods below send forms (or gets) to the web ui.
    """

    @classmethod
    def set_mhpearl_settings(
            cls, client,
            device_name='',       # device name for mh admin
            device_channel='',    # vod recorder id number
            file_search_range_in_seconds='',    # range within which it must
                                                # locate a recording
            admin_server_url='',  # mh admin url
            admin_server_usr='',  # mh digest user
            admin_server_pwd='',  # mh digest pwd
            update_frequency_in_seconds='120',  # freq to poll for schedule
            backup_agent=False):    # if True, does not upload recording to
                                    # mh when done

        check_success = [
                {
                    'emsg': 'device_name expected(%s)' % device_name,
                    'func': WebUiConfig.check_input_id_value(
                        tag_id='ca_name', value=device_name)},
                {
                    'emsg': 'device_username expected(%s)' % client.user,
                    'func': WebUiConfig.check_input_id_value(
                        tag_id='ca_user', value=client.user)},
                {
                    'emsg': 'not the device_password expected',
                    'func': WebUiConfig.check_input_id_value(
                        tag_id='ca_pass', value=client.passwd)},
                {
                    'emsg': 'device_channel expected(%s)' % device_channel,
                    'func': WebUiConfig.check_input_id_value(
                        tag_id='ca_chan', value=device_channel)},
                {
                    'emsg': 'file_search_range expected(%s)' %
                            file_search_range_in_seconds,
                    'func': WebUiConfig.check_input_id_value(
                        tag_id='ca_range',
                        value=str(file_search_range_in_seconds))},
                {
                    'emsg': 'admin_server_url expected(%s)' % admin_server_url,
                    'func': WebUiConfig.check_input_id_value(
                        tag_id='mh_host', value=admin_server_url)},
                {
                    'emsg': 'admin_server_user expected(%s)' %
                            admin_server_usr,
                    'func': WebUiConfig.check_input_id_value(
                        tag_id='mh_user', value=admin_server_usr)},
                {
                    'emsg': 'not the admin_server_passwd expected',
                    'func': WebUiConfig.check_input_id_value(
                        tag_id='mh_pass', value=admin_server_pwd)},
                {
                    'emsg': 'update_frequency expected(%s)' %
                            update_frequency_in_seconds,
                    'func': WebUiConfig.check_input_id_value(
                        tag_id='mh_freq',
                        value=str(update_frequency_in_seconds))}]

        params = {
                'DEVICE_NAME': device_name,
                'DEVICE_USERNAME': client.user,
                'DEVICE_PASSWORD': client.passwd,
                'DEVICE_CHANNEL': device_channel,
                'FILE_SEARCH_RANGE': file_search_range_in_seconds,
                'ADMIN_SERVER_URL': admin_server_url,
                'ADMIN_SERVER_USER': admin_server_usr,
                'ADMIN_SERVER_PASSWD': admin_server_pwd,
                'UPDATE_FREQUENCY': update_frequency_in_seconds}

        if backup_agent:
            params['BACKUP_AGENT'] = 'on'
            check_success.append({
                'emsg': 'backup_agent expected("ON")',
                'func': WebUiConfig.check_singlevalue_checkbox(
                    tag_id='mh_backup')})
        else:
            check_success.append({
                'emsg': 'backup_agent expected("ON")',
                'func': WebUiConfig.
                        check_singlevalue_checkbox_disabled(
                            tag_id='mh_backup')})

        path = '/admin/mhcfg'
        return WebUiConfig.configuration(
                client=client,
                params=params,
                path=path,
                check_success=check_success)
