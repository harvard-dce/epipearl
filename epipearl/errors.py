# -*- coding: utf-8 -*-
"""exception for epipearl cadash."""

__all__ = [
        'EpipearlError',
        'SettingConfigError',
        'IndiscernibleResponseFromWebUiError'
        ]


class EpipearlError(Exception):
    """base class to all exceptions raised by this module."""


class SettingConfigError(EpipearlError):
    """error in settings configs, usually benign warnings."""


class IndiscernibleResponseFromWebUiError(EpipearlError):
    """unexpected result from epiphan device; call failed"""
