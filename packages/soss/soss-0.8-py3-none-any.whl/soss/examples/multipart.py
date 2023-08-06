# -*- coding: utf-8 -*-
import json
from ast import literal_eval

import xmltodict

from soss.api import JrssAPI
from soss.utils.ossutils import get_part_xml, GetMultipartUploadsXml, GetPartsXml, GetInitUploadIdXml
from soss.utils.xmlutils import ErrorXml, GetBucketLocationXml, DeleteObjectsXml, \
    GetServiceXml

HOST = ""
ACCESS_ID = ""
SECRET_ACCESS_KEY = ""

jrss = JrssAPI(HOST, ACCESS_ID, SECRET_ACCESS_KEY)

if __name__ == '__main__':

    #
    # Todo: Multipart
    # Todo: InitiateMultipartUpload
    bucket = 'v06'
    object = 'v.sh'
    res = jrss.init_multi_upload(bucket, object)
    ret = literal_eval(json.dumps(xmltodict.parse(res.read()), indent=2)) if res.status == 200 else res.status
    print(ret)
    upload_id = ret['InitiateMultipartUploadResult']['UploadId']

    # Todo: UploadPart
    # Upload a part
    # Multipart Upload 要求除最后一个 Part 以外，其他的 Part 大小都要大于 100KB。但是 Upload
    # Part 接口并不会立即校验上传 Part 的大小（因为不知道是否为最后一块）；只有当 Complete
    # Multipart Upload 的时候才会校验
    # Todo: UploadPart 从字符串
    res = jrss.upload_part_from_string(bucket, object, 'first part', upload_id, '1')
    print(res.status)

    # Upload another part
    res = jrss.upload_part_from_string(bucket, object, '\n another part', upload_id, '1')
    print(res.status)

    # Verify: Get all parts
    res = jrss.get_all_parts(bucket, object, upload_id)
    content = res.read()
    ret = GetPartsXml(content).list() if res.status == 200 else res.status
    print(ret)
    print((literal_eval(json.dumps(xmltodict.parse(content)))))

    # Verify: Complete MultipartUpload
    part_msg_xml = get_part_xml(jrss, bucket, object, upload_id)
    res = jrss.complete_upload(bucket, object, upload_id, part_msg_xml)
    ret = literal_eval(json.dumps(xmltodict.parse(res.read()))) if res.status == 200 else ErrorXml(res.read()).show()
    print(ret)

    # Verify: GetObject
    res = jrss.get_object(bucket, object)
    ret = res.read() if res.status == 200 else ErrorXml(res.read()).show()
    print(ret)

    # Todo: UploadPart 从文件Offset
    bucket = 'v06'
    object = 'tbl02'
    filename = '/etc/hosts'
    res = jrss.init_multi_upload(bucket, object)
    iu = GetInitUploadIdXml(res.read())
    if res.status == 200:
        upload_id = iu.upload_id

    res = jrss.upload_part_from_file_given_pos(bucket, object, filename, 12, 36, upload_id, '1')
    print(res.status)
    # Verify: Complete MultipartUpload
    part_msg_xml = get_part_xml(jrss, bucket, object, upload_id)
    res = jrss.complete_upload(bucket, object, upload_id, part_msg_xml)
    ret = literal_eval(json.dumps(xmltodict.parse(res.read()))) if res.status == 200 else ErrorXml(res.read()).show()
    print(ret)
    # Verify: GetObject
    res = jrss.get_object(bucket, object)
    ret = res.read() if res.status == 200 else ErrorXml(res.read()).show()
    print(ret)

    # Todo: UploadPart 从文件
    bucket = 'v06'
    object = 'tbl02'
    filename = '/rd/sosstest_jrss/tbl01.txt'
    res = jrss.init_multi_upload(bucket, object)
    iu = GetInitUploadIdXml(res.read())
    if res.status == 200:
        upload_id = iu.upload_id

    # Todo: DeleteMultipleObject
    res = jrss.multi_upload_file(bucket, object, filename, upload_id)
    ret = literal_eval(json.dumps(xmltodict.parse(res.read()))) if res.status == 200 else ErrorXml(res.read()).show()
    print(ret)
    # Verify: GetObject
    res = jrss.get_object(bucket, object)
    ret = res.read() if res.status == 200 else ErrorXml(res.read()).show()
    print(ret.decode())
    # Verify: ListObjects
    object_list = jrss.list_objects(bucket)
    print(object_list)

    # Verify: DeleteObjects
    res = jrss.delete_objects(bucket, object_list)
    print(res.status)
    print(res.getheaders())
    gs = DeleteObjectsXml(res.read())
    gs.show()

    # Verify: GetService
    res = jrss.get_service()
    ret = GetServiceXml(res.read()).show() if res.status == 200 else res.status
    print(ret)

    # Verify: DeleteBucket
    bucket = 'testbucket'
    res = jrss.put_bucket_acl(bucket, grant_full_control='id="sosstest"')
    if res.status == 200:
        res = jrss.delete_bucket(bucket)
        ret = GetBucketLocationXml(res.read()).show() if res.status == 200 else ErrorXml(res.read()).show()
        print(ret)

    # Todo: CompleteMultipartUpload
    part_msg_xml = get_part_xml(jrss, bucket, object, upload_id)
    res = jrss.complete_upload(bucket, object, upload_id, part_msg_xml)
    ret = literal_eval(json.dumps(xmltodict.parse(res.read()))) if res.status == 200 else ErrorXml(res.read()).show()
    print(ret)

    # Todo: AbortMultipartUpload
    res = jrss.get_all_multipart_uploads(bucket)
    if res.status == 200:
        mu = GetMultipartUploadsXml(res.read())
        for e in mu.content_list:
            res = jrss.cancel_upload(bucket, e.key, e.upload_id)
            print(res.status)

    # Todo: ListMultipartUploads
    res = jrss.get_all_multipart_uploads(bucket)
    ret = GetMultipartUploadsXml(res.read()).list() if res.status == 200 else res.status
    print(ret)

    # Todo: ListParts
    res = jrss.get_all_parts(bucket, object, upload_id)
    content = res.read()
    ret = GetPartsXml(content).list() if res.status == 200 else res.status
    print(ret)
    print((literal_eval(json.dumps(xmltodict.parse(content)))))
