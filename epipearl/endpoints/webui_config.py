# -*- coding: utf-8 -*-
"""http api and web ui calls to epiphan pearl."""

from bs4 import BeautifulSoup
import logging

from epipearl.errors import IndiscernibleResponseFromWebUiError
from epipearl.errors import SettingConfigError


class WebUiConfig(object):
    """calls to epiphan pearl web ui.

    these are not non-documented calls, so can break if epiphan
    changes its webui interface. and beware that these are design
    to fit dce config reqs!

    use at your own peril!!!!

    methods below send forms (or gets) to the web ui.
    """

    @classmethod
    def check_singlevalue_checkbox(cls, tag_id):
        def f(tag):
            return tag.has_attr('id') and \
                    tag['id'] == tag_id and \
                    tag.has_attr('checked')
        return f

    @classmethod
    def check_singlevalue_checkbox_disabled(cls, tag_id):
        def f(tag):
            return tag.has_attr('id') and \
                    tag['id'] == tag_id and \
                    not tag.has_attr('checked')
        return f

    @classmethod
    def check_singlevalue_select(cls, value):
        def f(tag):
            return tag.has_attr('selected') and \
                    tag.has_attr('value') and \
                    tag['value'] == value
        return f

    @classmethod
    def check_multivalue_select(cls, name, value):
        def f(tag):
            return tag.has_attr('checked') and \
                    tag.has_attr('name') and \
                    tag['name'] == name and \
                    tag['value'] == value
        return f

    @classmethod
    def check_input_id_value(cls, tag_id, value):
        def f(tag):
            return tag.has_attr('id') and \
                    tag['id'] == tag_id and \
                    tag['value'] == value
        return f


    @classmethod
    def set_ntp(cls, client, server, timezone):
        params = {
                'server': server, 'tz': timezone,
                'fn': 'date', 'rdate': 'auto', 'rdate_proto': 'NTP',
                'rdate_secs': '900', 'ptp_domain': '_DFLT'}

        check_success = [
                {
                    'emsg': 'timezone setting expected(%s)' % timezone,
                    'func': cls.check_singlevalue_select(
                        value=timezone)},
                {
                    'emsg': 'protocol setting expected(NTP)',
                    'func': cls.check_singlevalue_select(
                        value='NTP')},
                {
                    'emsg': 'expected to enable sync(auto)',
                    'func': cls.check_singlevalue_checkbox(
                        tag_id='rdate_auto')},
                {
                    'emsg': 'expected ntp server(%s)' % server,
                    'func': cls.check_input_id_value(
                        tag_id='server', value=server)}]
        return cls.configuration(
                client=client,
                path='admin/timesynccfg',
                params=params,
                check_success=check_success)


    @classmethod
    def set_touchscreen(cls, client, screen_timeout=600):
        params = {
                'pdf_form_id': 'fn_episcreen',
                'epiScreenTimeout': screen_timeout,
                'changeSettings': 'on',
                'recordControl': '',
                'showVideo': 'on',
                'epiScreenEnable': 'on',
                'showInfo': 'on'}

        check_success = [
                {
                    'emsg': 'epiScreenEnable ON expected',
                    'func': cls.check_singlevalue_checkbox(
                        tag_id='epiScreenEnable')},
                {
                    'emsg': 'showPreview ON expected',
                    'func': cls.check_singlevalue_checkbox(
                        tag_id='showVideo')},
                {
                    'emsg': 'showSystemStatus ON expected',
                    'func': cls.check_singlevalue_checkbox(
                        tag_id='showInfo')},
                {
                    'emsg': 'changeSettings ON expected',
                    'func':
                        cls.check_singlevalue_checkbox(
                            tag_id='changeSettings')},
                {
                    'emsg': 'recordControl OFF expected',
                    'func':
                        cls.check_singlevalue_checkbox_disabled(
                            tag_id='recordControl')},
                {
                    'emsg': 'epiScreenTimeout expected(%s)' % screen_timeout,
                    'func': cls.check_input_id_value(
                        tag_id='epiScreenTimeout', value=str(screen_timeout))}]

        return cls.configuration(
                client=client,
                path='admin/touchscreencfg',
                params=params,
                check_success=check_success)

    @classmethod
    def set_remote_support_and_permanent_logs(cls, client, log_enabled=True):
        _default_server = 'epiphany.epiphan.com'
        _default_port = '30'

        params = {
                'fn': 'maint',
                'enablessh': 'on',
                'tunnel': 'on',
                'tunnelsrv': _default_server,
                'tunnelport': _default_port}

        check_success = [
                # TODO: figure how to check for success
                # remotesupport.cgi does not respond the same html form,
                # sends a META HTTP-EQUIV with redirection instead...
                ]

        if log_enabled:
            params['permanent_logs'] = 'on'
        else:
            params['permanent_logs'] = ''

        return cls.configuration(
                client=client,
                path='admin/remotesupport.cgi',
                params=params,
                check_success=check_success)


    @classmethod
    def update_firmware(cls, client, params, check_success):
        raise NotImplementedError('update_firmware() not implemented yet.')

    @classmethod
    def set_afu(cls, client):
        raise NotImplementedError(
                'set_automatic_file_upload() not implemented yet.')

    @classmethod
    def set_upnp(cls, client):
        raise NotImplementedError(
                'set_universal_plug_and_play() not implemented yet.')

    @classmethod
    def set_source_deinterlacing(cls, client, source_name, enabled=True):
        params = {'pfd_form_id': 'vsource'}
        check_success = []

        if enabled:
            params['deinterlacing'] = 'on'
            check_success.append(
                {
                    'emsg': 'deinterlacing expected to be ON',
                    'func': cls.check_singlevalue_checkbox(
                        tag_id='deinterlacing')})
        else:
            params['deinterlacing'] = ' '
            check_success.append(
                {
                    'emsg': 'deinterlacing expected to be OFF',
                    'func':
                        cls.check_singlevalue_checkbox_disabled(
                            tag_id='deinterlacing')})

        return cls.configuration(
                client=client,
                path='admin/sources/%s' % source_name,
                params=params,
                check_success=check_success)


    @classmethod
    def configuration(cls, client, params, check_success, path):
        """generic request to config form

        client: epipearl client instance
        path: for webui function, ex: admin/timesynccfg
        params: dict with params for web ui form
        check_success: list of dicts
            [{ 'func': <function for BeautifulSoup.find>
               'emsg': string error msg if func returns false }]
        """
        r = client.post(
                path, data=params,
                extra_headers={
                    'Content-Type': 'application/x-www-form-urlencoded'})

        msg = 'error from call %s/%s ' % (client.url, path)
        logger = logging.getLogger(__name__)
        # still have to check errors in response html
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            emsg = cls._scrape_error(soup)
            if len(emsg) > 0:     # concat error messages
                allmsgs = [x['msg'] for x in emsg if 'msg' in x]
                msg += '\n'.join(allmsgs)
                logger.error(msg)
                raise SettingConfigError(msg)
            else:
                # no error msg, check that updates took place
                for c in check_success:
                    tags = soup.find_all(c['func'])
                    if not tags:
                        msg += '- %s' % c['emsg']
                        logger.error(msg)
                        raise SettingConfigError(msg)
            # all is well
            return True

        msg = 'error in call %s/%s - response status(%s)' % (
                client.url, path, r.status_code)
        logging.getLogger(__name__).error(msg)
        raise IndiscernibleResponseFromWebUiError(msg)


    @classmethod
    def _scrape_error(cls, soup):
        """webscrape for error msg in returned html."""
        warn = soup('div', class_='wui-message-warning')
        msgs = cls._scrape_msg(warn)
        error = soup('div', class_='wui-message-error')
        msgs += cls._scrape_msg(error, warning=False)
        return msgs


    @classmethod
    def _scrape_msg(cls, mtag, warning=True):
        """navigate div to find msg text and error code."""
        resp = []
        if len(mtag) > 0:
            dtag = mtag[0].findChildren(
                    'div',
                    class_='wui-message-banner-inner')
            for d in dtag:
                lines = d.strings
                error_msg = None
                error_code = None
                try:
                    error_msg = next(lines)
                    error_code = next(lines)
                except StopIteration:
                    # msg or code or both not found!
                    pass
                except Exception as e:
                    msg = 'could not scrape epiphan webui response: %s' \
                            % e.message
                    logging.getLogger(__name__).error(msg)
                    resp.append({
                        'cat': 'error',
                        'msg': msg,
                        'code': 'html_parsing_error'})
                else:
                    # msg and code ok
                    resp.append({
                        'cat': 'warning' if warning else 'error',
                        'msg': error_msg if error_msg else 'unknown msg',
                        'code': error_code if error_code else 'unknown code'})
        return resp
