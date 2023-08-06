# coding: utf-8
import hashlib


def sign(param, appsecret, signmethod):
    if signmethod != "MD5":
        return ''

    lists = []
    param_str = appsecret
    for item in param:
        lists.append(item)

    lists.sort()

    for key in lists:
        if param[key] is None or param[key] == '':
            continue
        param_str = param_str + key + str(param[key])

    param_str += appsecret
    param_str = param_str.strip()

    return genMd5(param_str)


def genMd5(str):
    md5 = hashlib.md5()
    md5.update(str)
    md5.hexdigest()
    return md5.hexdigest()
