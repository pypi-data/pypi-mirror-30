# -*- coding: utf-8 -*-
from soss.api import JrssAPI
from soss.utils.xmlutils import GetBucketAclXml, ErrorXml, GetBucketLocationXml, GetBucketXml

HOST = ""
ACCESS_ID = ""
SECRET_ACCESS_KEY = ""

jrss = JrssAPI(HOST, ACCESS_ID, SECRET_ACCESS_KEY)

if __name__ == '__main__':
    # Todo: PutBucket
    # 创建Bucket
    bucket = 'v06'
    res = jrss.create_bucket(bucket, grant_read='id="sosstest"', grant_full_control='id="sosstest"', location='cn-bj')
    print(res.status)

    # Todo: GetBucket
    # 列出Bucket中所有Object信息
    res = jrss.get_bucket(bucket)
    ret = GetBucketXml(res.read()).show() if res.status == 200 else res.status
    print(ret)

    # Todo: PutBucketACL
    # 授权方式：request body中授权
    acl_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <AccessControlPolicy>
        <Owner>
            <ID>sosstest</ID>
            <DisplayName>sosstest</DisplayName>
        </Owner>
        <AccessControlList>
            <Grant>
                <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                    <ID>sosstest</ID>
                    <DisplayName>sosstest</DisplayName>
                </Grantee>
                <Permission>FULL_CONTROL</Permission>
            </Grant>
        </AccessControlList>
    </AccessControlPolicy>'''
    res = jrss.put_bucket_acl(bucket, acl_xml=acl_xml)
    ret = res.status if res.status == 200 else ErrorXml(res.read())
    print(ret)

    # 授权方式：Grant 请求头授权
    jrss.put_bucket_acl(bucket, grant_read='id="sosstest"')
    jrss.put_bucket_acl(bucket, grant_write='id="sosstest"')
    jrss.put_bucket_acl(bucket, grant_read_acp='id="sosstest"')
    jrss.put_bucket_acl(bucket, grant_write_acp='id="sosstest"')
    jrss.put_bucket_acl(bucket, grant_full_control='id="sosstest"')
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

    # Todo: HeadBucket
    # 获取某个 Bucket 下的 object 个数和 object 总大小
    res = jrss.head_bucket(bucket)
    print((res.getheaders()))
