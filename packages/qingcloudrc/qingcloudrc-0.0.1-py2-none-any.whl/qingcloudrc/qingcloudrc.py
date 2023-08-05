# -*- coding: utf-8 -*-

import base64
import hmac
import urllib
import os
import sys
from hashlib import sha256

def run_instance(instance_name='rctest',access_key_id='BPAGNZITTCAZDQWOKDBK', secret_access_key='WKqCnFZMXxeGZDMHqn6NDep1bMtXRg0IHlpYEcyy', config_path = ''):

    if os.path.exists(config_path) and not access_key_id and not secret_access_key :
        with open(config_path, 'r') as f:
            login_info = f.readlines()
            access_key_id_tmp = login_info[0]
            secret_access_key_tmp = login_info[1]
    else:
        access_key_id_tmp = access_key_id
        secret_access_key_tmp = secret_access_key

    string_to_sign = 'GET\n/iaas/\naccess_key_id=' + access_key_id + '&action=RunInstances&count=1&image_id=centos73x64&instance_name='+ instance_name+ '&instance_type=c1m1&login_mode=passwd&login_passwd=Test123456&signature_method=HmacSHA256&signature_version=1&time_stamp=2018-05-30T05%3A05%3A10Z&version=1&vxnets.1=vxnet-0&zone=pek3b'
    h = hmac.new(secret_access_key_tmp, digestmod=sha256)
    h.update(string_to_sign)
    sign = base64.b64encode(h.digest()).strip()
    signature = urllib.quote_plus(sign)
    #用户的资源信息应该保持在一张表中，此处可以查询得出
    url = 'https://api.qingcloud.com/iaas/?access_key_id=' + access_key_id_tmp + '&action=RunInstances&count=1&image_id=centos73x64&instance_name='+ instance_name+ '&instance_type=c1m1&login_mode=passwd&login_passwd=Test123456&signature_method=HmacSHA256&signature_version=1&time_stamp=2018-05-30T05%3A05%3A10Z&version=1&vxnets.1=vxnet-0&zone=pek3b&signature=' + signature
    response = urllib.urlopen(url)
    return response.read()


if __name__ == '__main__':
    # path = r'F:\pyCode\qingcloud\config.txt'
    #instance_name = sys.argv[1]
    #access_key_id = sys.argv[2]
    #secret_access_key = sys.argv[3]
    #res = run_instance(instance_name,access_key_id,secret_access_key)
    res = run_instance('rctest', 'BPAGNZITTCAZDQWOKDBK', 'WKqCnFZMXxeGZDMHqn6NDep1bMtXRg0IHlpYEcyy','')
    print(res)
    #fire.Fire(Test)