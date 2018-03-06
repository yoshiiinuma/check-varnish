#!/usr/bin/env python

'''
usage: sudo varnishlog | python check-varnish.py [--all]
'''

import sys
import re

only_miss = True
if len(sys.argv) == 2 and sys.argv[1] == '--all':
    only_miss = False

req_method = re.compile(r"ReqMethod +([^ ]+)")
req_url = re.compile(r"ReqURL +([^ ]+)")
res_status = re.compile(r"RespStatus +([^ ]+)")
res_reason = re.compile(r"RespReason +([^ ]+)")
vcl_call = re.compile(r"VCL_call +([^ ]+)")
vcl_return = re.compile(r"VCL_return +([^ ]+)")
x_cache = re.compile(r"X-Cache: +([^ ]+)")
set_cookie = re.compile(r"RespHeader +Set-Cookie: (.+)$")
cache_control = re.compile(r"RespHeader +Cache-Control: (.+)$")
age = re.compile(r"RespHeader +Age: ([^ ]+)")
sess_begin = re.compile(r"^- +Begin")
sess_end = re.compile(r"^- +End")

def display(r):
    if not 'ReqURL' in r:
        return
    if only_miss:
        if 'X-Cache' in r and r['X-Cache'] != 'MISS':
            return
    print('{X-Cache:4} {ReqMethod:5} {RespStatus} {ReqURL}'.format(**r))

def main():
    key = ''
    r = {}
    l = sys.stdin.readline()
    while l:
        l = l.strip()
        #if re.match(sess_begin, l):
        #    r = {}
        #    l = sys.stdin.readline()
        #    continue
        m = re.search(req_method, l)
        if m:
            r['ReqMethod'] = m.group(1)
        m = re.search(req_url, l)
        if m:
            r['ReqURL'] = m.group(1)
        m = re.search(vcl_call, l)
        if m:
            key = m.group(1)
        m = re.search(vcl_return, l)
        if m:
            if key:
                r[key] = m.group(1)
        m = re.search(res_status, l)
        if m:
            r['RespStatus'] = m.group(1)
        m = re.search(res_reason, l)
        if m:
            r['RespReason'] = m.group(1)
        m = re.search(set_cookie, l)
        if m:
            r['Set-Cookie'] = m.group(1)
        m = re.search(cache_control, l)
        if m:
            r['Cache-Control'] = m.group(1)
        m = re.search(age, l)
        if m:
            r['Age'] = m.group(1)
        m = re.search(x_cache, l)
        if m:
            r['X-Cache'] = m.group(1)
        if re.search(sess_end, l):
            if r:
                display(r)
            r = {}
        l = sys.stdin.readline()

if __name__ == '__main__':
    main()
