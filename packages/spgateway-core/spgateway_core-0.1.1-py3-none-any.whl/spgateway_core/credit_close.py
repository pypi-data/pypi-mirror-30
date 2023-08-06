import json
import logging
import time
from collections import OrderedDict
from urllib import urlencode

import requests

from .consts import CREDIT_CLOSE_URL
from .utils import TRUE_TUPLE, encrypt_info

logger = logging.getLogger(__name__)


def generate_post_data_from_dict(trade_info_dict):
    order_tuple = (
        'RespondType', 'TimeStamp', 'Version',
        'CloseType', 'Amt',
        'IndexType', 'MerchantOrderNo', 'TradeNo',
        'Cancel'
    )

    message_list = list()
    for each_key in order_tuple:
        value = trade_info_dict.get(each_key)
        if value is not None:
            message_list.append((each_key, value))
    for each_key in trade_info_dict.keys():
        if each_key not in order_tuple and value is not None:
            if value is not None:
                message_list.append((each_key, value))

    ordered_message = OrderedDict(message_list)
    post_data = urlencode(ordered_message)

    return post_data


def generate_post_data_dict(
        Amt,

        MerchantOrderNo=None,
        TradeNo=None,

        RespondType='JSON',
        Version='1.0',

        TimeStamp=None,
        IndexType=1,

        CloseType=1,
        Cancel=None,
):
    post_data_dict = dict()
    post_data_dict['Amt'] = int(Amt)
    post_data_dict['TimeStamp'] = TimeStamp or int(time.time())
    post_data_dict['RespondType'] = RespondType or 'JSON'
    post_data_dict['Version'] = Version or '1.0'

    if IndexType is not None:
        post_data_dict['IndexType'] = int(IndexType) if IndexType in (1, '1', 2, '2') else 1
    else:
        post_data_dict['IndexType'] = 1

    if CloseType is not None:
        post_data_dict['CloseType'] = int(IndexType) if IndexType in (1, '1', 2, '2') else 1
    else:
        post_data_dict['CloseType'] = 1

    if Cancel is not None:
        post_data_dict['Cancel'] = 1 if Cancel in TRUE_TUPLE else None

    if post_data_dict['IndexType'] == 1:
        if MerchantOrderNo is None:
            raise ValueError('MerchantOrderNo not offered.')
        else:
            post_data_dict['MerchantOrderNo'] = str(MerchantOrderNo)[:20]

    if post_data_dict['IndexType'] == 2:
        if TradeNo is None:
            raise ValueError('TradeNo not offered.')
        else:
            post_data_dict['TradeNo'] = str(TradeNo)[:20]

    return post_data_dict


class CreditCloseClient(object):
    def __init__(self, merchant_id, hash_key, hash_iv, credit_close_url=None):
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.credit_close_url = credit_close_url or CREDIT_CLOSE_URL

    def execute(self, **kwargs):
        post_data = generate_post_data_from_dict(generate_post_data_dict(**kwargs))
        encrypted_post_data = encrypt_info(hash_iv=self.hash_iv, hash_key=self.hash_key, info=post_data)

        data = dict(
            MerchantID_=self.merchant_id,
            PostData_=encrypted_post_data
        )

        response = requests.post(self.credit_close_url, data)

        return json.loads(response.text)
