# -*- coding: utf-8 -*-
"""
Author: Deyou Lee(lideyou) <deyoulee@126.com>
"""
import json
from ast import literal_eval

import xmltodict

from soss.api import *
from soss.utils.xmlutils import *

# HOST = "pre-jrss-hb.jdfcloud.com"
# ACCESS_ID = "S2BHRFXY6BM682NZQ9AA"
# SECRET_ACCESS_KEY = "LoWqLJDNR99Hq1TFKS2Np9KDjBg7FdC1Sii28d3D"

# liujinzhou
HOST = "pre-jrss-hb.jdfcloud.com"
ACCESS_ID = "BW6Y9ZZXVRFLBZEB8T93"
SECRET_ACCESS_KEY = "z6VWzBUOiwF8C5Xm0uNepoa3QUbODzpRl1ogebTz"
jrss = JrssAPI(HOST, ACCESS_ID, SECRET_ACCESS_KEY)

#
# Todo: GetService
# 返回请求者拥有的所有Bucket
res = jrss.get_service()
ret = GetServiceXml(res.read()).show() if res.status == 200 else res.status
print(ret)

#
# Todo: PutBucket
# 创建Bucket
bucket = 'v08'
res = jrss.create_bucket(bucket, grant_read='id="liujinzhou"', grant_full_control='id="liujinzhou"', location='cn-bj')
print(res.status)

# Todo: GetBucket
# 列出Bucket中所有Object信息
res = jrss.get_bucket(bucket)
ret = GetBucketXml(res.read()).show() if res.status == 200 else res.status
print(ret)

#
# Todo: PutBucketACL
# 授权方式：request body中授权
acl_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<AccessControlPolicy>
    <Owner>
        <ID>liujinzhou</ID>
        <DisplayName>liujinzhou</DisplayName>
    </Owner>
    <AccessControlList>
        <Grant>
            <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Group">
                <URI>http://acs.amazonaws.com/groups/global/AllUsers</URI>
            </Grantee>
            <Permission>READ</Permission>
        </Grant>
        <Grant>
            <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Group">
                <URI>http://acs.amazonaws.com/groups/global/AllUsers</URI>
            </Grantee>
            <Permission>WRITE</Permission>
        </Grant>
        <Grant>
            <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                <ID>liujinzhou</ID>
                <DisplayName>liujinzhou</DisplayName>
            </Grantee>
            <Permission>FULL_CONTROL</Permission>
        </Grant>
    </AccessControlList>
</AccessControlPolicy>'''
res = jrss.put_bucket_acl(bucket, acl_xml=acl_xml)
ret = res.status if res.status == 200 else ErrorXml(res.read())
print(ret)

# 授权方式：Grant 请求头授权
jrss.put_bucket_acl(bucket, grant_read='id="liujinzhou"')
jrss.put_bucket_acl(bucket, grant_write='id="liujinzhou"')
jrss.put_bucket_acl(bucket, grant_read_acp='id="liujinzhou"')
jrss.put_bucket_acl(bucket, grant_write_acp='id="liujinzhou"')
jrss.put_bucket_acl(bucket, grant_full_control='id="liujinzhou"')
ret = res.status if res.status == 200 else ErrorXml(res.read()).show()
print(ret)

# 授权方式：Canned ACL
jrss.put_bucket_acl(bucket, acl='private')
jrss.put_bucket_acl(bucket, acl='public-read')
jrss.put_bucket_acl(bucket, acl='public-read-write')
jrss.put_bucket_acl(bucket, acl='authenticated-read')
jrss.put_bucket_acl(bucket, acl='bucket-owner-read')
res = jrss.put_bucket_acl(bucket, acl='bucket-owner-full-control')
ret = res.status if res.status == 200 else ErrorXml(res.read()).show()
print(ret)

# Todo: GetBucktACL
# 获取某个Bucket的访问权限
res = jrss.get_bucket_acl(bucket)
ret = GetBucketAclXml(res.read()).show() if res.status == 200 else ErrorXml(res.read()).show()
print(ret)

# Todo: GetBucketLocation
# 查看Bucket所属的region位置信息
res = jrss.get_bucket_location(bucket)
GetBucketLocationXml(res.read()).show() if res.status == 200 else ErrorXml(res.read()).show()

# Todo: DeleteBucket
bucket = 'v06'
res = jrss.delete_bucket(bucket)
ret = res.status if res.status == 204 else ErrorXml(res.read()).show()
print(ret)

# Todo: HeadBucket 错误: 返回为空=========================
# 获取某个 Bucket 下的 object 个数和 object 总大小
res = jrss.head_bucket(bucket)
print((res.getheaders()))


#
# Todo: PutObject from string
# 上传文件， 单个文件最大 5G
bucket = 'v08'
jrss.put_object_with_data(bucket, 'readme01', 'Seer, ML platform. \n Hello world')
jrss.put_object_with_data(bucket, 'readme02', 'Seer, ML platform. \n Hello world')
jrss.put_object_with_data(bucket, 'readme03', 'Seer, ML platform. \n Hello world')
res = jrss.put_object_with_data(bucket, 'readme.txt', 'Seer, ML platform. \n Hello world!')
print(res.status)

# Todo: GetObject
res = jrss.get_object(bucket, 'readme.txt')
ret = res.read() if res.status == 200 else ErrorXml(res.read()).show()
print(ret)