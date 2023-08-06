# -*- coding: utf-8 -*-
import json
from ast import literal_eval

import xmltodict

from soss.api import JrssAPI
from soss.utils.xmlutils import ErrorXml, GetBucketXml, DeleteObjectsXml

HOST = ""
ACCESS_ID = ""
SECRET_ACCESS_KEY = ""

jrss = JrssAPI(HOST, ACCESS_ID, SECRET_ACCESS_KEY)

if __name__ == '__main__':

    #
    # Todo: PutObject from string
    # 上传文件， 单个文件最大 5G
    bucket = 'v06'
    jrss.put_object_with_data(bucket, 'readme01', 'Seer, ML platform. \n Hello world')
    jrss.put_object_with_data(bucket, 'readme02', 'Seer, ML platform. \n Hello world')
    jrss.put_object_with_data(bucket, 'readme03', 'Seer, ML platform. \n Hello world')
    res = jrss.put_object_with_data(bucket, 'readme.txt', 'Seer, ML platform. \n Hello world!')
    print(res.status)

    # Todo: GetObject
    res = jrss.get_object(bucket, 'readme.txt')
    ret = res.read() if res.status == 200 else ErrorXml(res.read()).show()
    print(ret)

    # Todo: GetObject to file
    res = jrss.get_object_to_file(bucket, 'readme.txt', 'readme')
    print(res.status)

    # Todo: PutObject from file
    res = jrss.put_object_from_file(bucket, 'tbl01', 'tbl01.txt')
    print(res.status)
    res = jrss.get_object(bucket, 'tbl01')
    ret = res.read() if res.status == 200 else ErrorXml(res.read()).show()
    print(ret.decode())

    # Todo: DeleteObject
    res = jrss.delete_object(bucket, 'readme.txt')
    print(res.status)
    res = jrss.get_bucket(bucket)
    ret = GetBucketXml(res.read()).show() if res.status == 200 else res.status
    print(ret)

    # Todo:
    # Todo: DeleteMultipleObject
    # AttributeError: '_hashlib.HASH' object has no attribute 'new'
    res = jrss.delete_objects(bucket, ['readme02', 'readme03'])
    if res.status == 200:
        print((DeleteObjectsXml(res.read()).show()))
        res = jrss.get_bucket(bucket)
        ret = GetBucketXml(res.read()).show() if res.status == 200 else res.status
        print(ret)

    # Todo: HeadObject
    res = jrss.head_object(bucket, 'readme01')
    ret = res.getheaders() if res.status == 200 else res.status
    print(ret)

    # Todo: GetObjectACL
    res = jrss.get_object_acl(bucket, 'readme01')
    ret = json.dumps(xmltodict.parse(res.read()), indent=2) if res.status == 200 else res.status
    print(ret)

    # Todo: PutObjectACL
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
                <Permission>WRITE</Permission>
            </Grant>
            <Grant>
                <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                    <ID>sosstest</ID>
                    <DisplayName>sosstest</DisplayName>
                </Grantee>
                <Permission>READ_ACP</Permission>
            </Grant>
        </AccessControlList>
    </AccessControlPolicy>'''
    res = jrss.put_object_acl(bucket, 'readme01', acl_xml=acl_xml)
    ret = res.status if res.status == 200 else ErrorXml(res.read()).show()
    print(ret)

    # Todo: PutObject 从文件offset
    res = jrss.put_object_from_file_given_pos(bucket, 'pos', 'pos.txt', 12, 29)
    if res.status == 200:
        res = jrss.get_object(bucket, 'pos')
        ret = res.read() if res.status == 200 else ErrorXml(res.read()).show()
        print(ret)

    # Todo: CopyObject
    res = jrss.copy_object(bucket, 'pos', bucket, 'pos1')
    if res.status == 200:
        ret = json.dumps(xmltodict.parse(res.read()), indent=2) if res.status == 200 else ErrorXml(res.read()).show()
        print(ret)
        res = jrss.get_object(bucket, 'pos1')
        ret = res.read() if res.status == 200 else ErrorXml(res.read()).show()
        print(ret)

    # Todo: GeBucket
    res = jrss.get_bucket(bucket)
    ret = json.dumps(xmltodict.parse(res.read()), indent=2) if res.status == 200 else res.status
    print(ret)

    # Todo: ListObjectsDirs: Key,Size,Lastmodified
    res = jrss.list_objects_dirs(bucket)
    print((literal_eval(json.dumps(res))))

    # Todo: ListObjects
    object_list = jrss.list_objects(bucket)
    print(object_list)
