# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pywe_sign import check_signature
from pywe_xml import xml_to_dict


__all__ = ['check_pay_notify']


def check_pay_notify(xml, check_sign=True, api_key=None, wx_configs=None, trade_cfg=None, trade_cfg_func=None, api_key_func=None):
    # XML -> Dict
    data = xml_to_dict(xml)
    if isinstance(data, basestring):
        return data, False

    if not check_sign:
        return data, True

    # Check Sign
    if not check_signature(data, api_key or (api_key_func and api_key_func(data)) or wx_configs.get(trade_cfg or (trade_cfg_func and trade_cfg_func(data)) or data.get('trade_type', ''), {}).get('apiKey')):
        return data, False

    # Return Code
    return_code = data.get('return_code', '')
    if return_code != 'SUCCESS':
        return data, False

    return data, True
