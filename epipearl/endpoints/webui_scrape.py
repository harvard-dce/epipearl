# -*- coding: utf-8 -*-
"""utilities for all epiphan pearl."""

from bs4 import BeautifulSoup
import logging


def can_handle_form_element(tag):
    return tag.name in ['input', 'select', 'textarea']


def filter_by_attr_name(tag_name):
    def f(tag):
        return tag.has_attr('name') and tag['name'] == tag_name
    return f


def pluck_form_values(bs4_form):
    """scrape values from form and return them in dict keyed by tag attr name.

    handles <input> (hidden, text, password, checkbox, radio),
        <select>,
        <textarea>
    always returns a _list_ of selected options for <select>
    """

    result = {}
    tags = bs4_form(can_handle_form_element)

    for t in tags:
        key = pick_name_for_tag(t)

        if key is None or key in result:
            # tag already processed (ex: radio group) or duplicate
            # or ignored because of missing name
            continue

        if t.name == 'input':
            result[key] = pluck_form_input(t, bs4_form)
        elif t.name == 'select':
            result[key] = pluck_form_select(t)
        elif t.name == 'textarea':
            result[key] = t.string
    return result


def pick_name_for_tag(tag):
    if tag.has_attr('name'):
        return tag['name']
    else:
        # in form context, un-named form elements won't be transferred
        # to the server in the http post.
        logging.getLogger(__name__).error(
                'ignoring form <{}> - missing name: '
                '{}'.format(tag.name, tag.prettify()))
        return None


def pluck_form_input(bs4_input, bs4_form):
    """scrape form <input> and returns value.

        handles hidden, text, password, submit, search, button,
            checkbox, radio
        needs form to process <input type='radio'> in the form context
    """
    t = bs4_input
    if t.has_attr('type'):
        t_type = t['type']

        if t_type == 'hidden' or t_type == 'text' or \
                t_type == 'password' or t_type == 'submit' or \
                t_type == 'search' or t_type == 'button':
            return t['value'] if t.has_attr('value') else 'unknown'

        elif t_type == 'checkbox':
            return True if t.has_attr('checked') else False

        elif t_type == 'radio':
            if t.has_attr('name'):
                # find all options for this radio group
                radio_group = bs4_form.find_all(
                        filter_by_attr_name(t['name']))

                for r in radio_group:
                    if r.has_attr('checked'):
                        if r.has_attr('value'):
                            return r['value']
                        else:
                            # TODO: what values can this assume?
                            return r.string

            else:  # no-name: assuming radio button is not part of a group
                if t.has_attr('value'):
                    if t.has_attr('checked'):
                        if t.has_attr('value'):
                            return t['value']
                        else:
                            # TODO: what values can this assume?
                            return t.string

    else:  # missing type
        logging.getLogger(__name__).error(
                'failed to process form <input> - missing type: '
                '{}'.format(t.prettify()))

    return None  # value 'not found'


def pluck_form_select(bs4_select):
    """scrape form <select> and returns list of selected options."""
    selected = []
    select_options = bs4_select.find_all('option')
    for opt in select_options:
        if opt.has_attr('selected'):
            if opt.has_attr('value'):
                selected.append(opt['value'])
            else:
                selected.append(None)

    return selected


#
# below are functions very specific to epiphan-pearl webui
# firmware version 3.15.3f
#

def scrape_error(bs4_doc):
    """webscrape for error msg in bs4 document."""
    warn = bs4_doc('div', class_='wui-message-warning')
    msgs = scrape_msg(warn)
    error = bs4_doc('div', class_='wui-message-error')
    msgs += scrape_msg(error, warning=False)
    return msgs


def scrape_msg(message_tag, warning=True):
    """navigate div to find msg text and error code."""
    resp = []
    if len(message_tag) > 0:
        dtag = message_tag[0].findChildren(
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
