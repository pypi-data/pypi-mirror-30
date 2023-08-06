# -*- coding: utf-8 -*-
from soss.api import JrssAPI
from soss.utils.xmlutils import GetServiceXml

HOST = ""
ACCESS_ID = ""
SECRET_ACCESS_KEY = ""

jrss = JrssAPI(HOST, ACCESS_ID, SECRET_ACCESS_KEY)

if __name__ == '__main__':
    # Todo: 返回请求者拥有的所有Bucket
    res = jrss.get_service()
    ret = GetServiceXml(res.read()).show() if res.status == 200 else res.status
