import logging
import time
from collections import OrderedDict
from datetime import datetime, timedelta, date
from urllib import urlencode

from .utils import TRUE_TUPLE
from . import consts

logger = logging.getLogger(__name__)


def generate_trade_info_from_dict(trade_info_dict):
    order_tuple = (
        'MerchantID', 'RespondType', 'TimeStamp', 'Version',
        'LangType',
        'MerchantOrderNo', 'Amt', 'ItemDesc',
        'TradeLimit', 'ExpireDate',
        'ReturnURL', 'NotifyURL', 'CustomerURL', 'ClientBackURL',
        'Email', 'EmailModify',
        'LoginType',
        'OrderComment',
        'CREDIT', 'InstFlag', 'CreditRed', 'UNIONPAY', 'WEBATM', 'VACC', 'CVS', 'BARCODE', 'P2G', 'CVSCOM',
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
    trade_info = urlencode(ordered_message)

    return trade_info


def generate_trade_info_dict(
        MerchantID, MerchantOrderNo, Amt, ItemDesc, Email,

        RespondType='JSON',
        TimeStamp=None,
        Version=consts.MPG_VERSION,

        LangType=None,

        TradeLimit=None,
        ExpireDate=None,
        LoginType=None,
        OrderComment=None,

        ReturnURL=None,
        NotifyURL=None,
        CustomerURL=None,
        ClientBackURL=None,

        EmailModify=False,

        CREDIT=None,
        InstFlag=None,
        CreditRed=None,
        UNIONPAY=None,
        WEBATM=None,
        VACC=None,
        CVS=None,
        BARCODE=None,
        P2G=None,
        CVSCOM=None,

        **kwargs
):
    trade_info_dict = dict()
    trade_info_dict['MerchantID'] = MerchantID
    trade_info_dict['RespondType'] = RespondType or 'JSON'
    trade_info_dict['TimeStamp'] = TimeStamp or int(time.time())
    trade_info_dict['Version'] = Version or consts.MPG_VERSION
    trade_info_dict['MerchantOrderNo'] = str(MerchantOrderNo.encode('utf-8'))[:consts.MAX_ORDER_LEN]
    trade_info_dict['Amt'] = int(Amt)
    trade_info_dict['ItemDesc'] = str(ItemDesc.encode('utf-8'))[:consts.MAX_ITEMDESC_LEN]
    trade_info_dict['Email'] = Email

    if LangType is not None:
        trade_info_dict['LangType'] = LangType
    if TradeLimit is not None:
        if TradeLimit is False:
            trade_info_dict['TradeLimit'] = 0
        else:
            trade_info_dict['TradeLimit'] = TradeLimit
    if ExpireDate is not None:
        if isinstance(ExpireDate, (datetime, date)):
            trade_info_dict['ExpireDate'] = ExpireDate.strftime(r'%Y%m%d')
        elif isinstance(ExpireDate, timedelta):
            trade_info_dict['ExpireDate'] = (datetime.now() + ExpireDate).strftime(r'%Y%m%d')
        elif isinstance(ExpireDate, str):
            trade_info_dict['ExpireDate'] = date.strftime(ExpireDate, r'%Y%m%d').strftime(r'%Y%m%d')
        elif ExpireDate is True:
            trade_info_dict['ExpireDate'] = (datetime.now() + timedelta(days=7)).strftime(r'%Y%m%d')
        else:
            raise ValueError('Unknown ExpireDate format.')

    if ReturnURL is not None:
        trade_info_dict['ReturnURL'] = ReturnURL
        if len(ReturnURL) > consts.MAX_URI_LEN:
            logger.warn('ReturnURL more than {} may not proper.'.format(consts.MAX_URI_LEN))

    if NotifyURL is not None:
        trade_info_dict['NotifyURL'] = NotifyURL
        if len(NotifyURL) > consts.MAX_URI_LEN:
            logger.warn('NotifyURL more than {} may not proper.'.format(consts.MAX_URI_LEN))

    if CustomerURL is not None:
        trade_info_dict['CustomerURL'] = CustomerURL
        if len(CustomerURL) > consts.MAX_URI_LEN:
            logger.warn('CustomerURL more than {} may not proper.'.format(consts.MAX_URI_LEN))

    if ClientBackURL is not None and ClientBackURL is not False:
        trade_info_dict['ClientBackURL'] = ClientBackURL
        if len(ClientBackURL) > consts.MAX_URI_LEN:
            logger.warn('ClientBackURL more than {} may not proper.'.format(consts.MAX_URI_LEN))

    if EmailModify is not None:
        trade_info_dict['EmailModify'] = 1 if EmailModify in TRUE_TUPLE else 0
    if LoginType is not None:
        trade_info_dict['LoginType'] = 1 if LoginType in TRUE_TUPLE else 0
    if OrderComment is not None:
        trade_info_dict['OrderComment'] = OrderComment[:consts.MAX_ORDERCOMMENT_LEN]

    if CREDIT is not None:
        trade_info_dict['CREDIT'] = 1 if CREDIT in TRUE_TUPLE else 0
    if InstFlag is not None:
        if InstFlag in (True, 1, '1'):
            trade_info_dict['InstFlag'] = '1'
        elif InstFlag in (False, 0, '0'):
            trade_info_dict['InstFlag'] = '0'
        elif isinstance(InstFlag, list):
            trade_info_dict['InstFlag'] = ','.join(InstFlag)
        else:
            trade_info_dict['InstFlag'] = InstFlag
    if CreditRed is not None:
        trade_info_dict['CreditRed'] = 1 if CreditRed in TRUE_TUPLE else 0
    if UNIONPAY is not None:
        trade_info_dict['UNIONPAY'] = 1 if UNIONPAY in TRUE_TUPLE else 0
    if WEBATM is not None:
        trade_info_dict['WEBATM'] = 1 if WEBATM in TRUE_TUPLE else 0
    if VACC is not None:
        trade_info_dict['VACC'] = 1 if VACC in TRUE_TUPLE else 0
    if CVS is not None:
        if CVS in (True, 1):
            trade_info_dict['CVS'] = 1
            if Amt < consts.MIN_CVS_AMT or Amt > consts.MAX_CVS_AMT:
                logger.warn(
                    'Amt less than {} or larger than {} would not be able to use CVS.'.format(
                        consts.MIN_CVS_AMT, consts.MAX_CVS_AMT
                    )
                )
        else:
            trade_info_dict['CVS'] = 0
    if BARCODE is not None:
        if BARCODE in (True, 1):
            trade_info_dict['BARCODE'] = 1
            if Amt < consts.MIN_BARCODE_AMT or Amt > consts.MAX_BARCODE_AMT:
                logger.warn(
                    'Amt less than {} or larger than {} would not be able to use BARCODE.'.format(
                        consts.MIN_BARCODE_AMT, consts.MAX_BARCODE_AMT
                    )
                )
        else:
            trade_info_dict['BARCODE'] = 0
    if P2G is not None:
        trade_info_dict['P2G'] = 1 if P2G in TRUE_TUPLE else 0
    if CVSCOM is not None:
        trade_info_dict['CVSCOM'] = int(CVSCOM)

    trade_info_dict.update(kwargs)

    return trade_info_dict
