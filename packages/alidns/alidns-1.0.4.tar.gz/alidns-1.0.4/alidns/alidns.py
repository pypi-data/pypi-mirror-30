#!/usr/bin/python3

from aliyunsdkcore import client
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest       import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DeleteDomainRecordRequest    import DeleteDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest    import UpdateDomainRecordRequest

from argparse import ArgumentParser
import json
import socket

class R:
    verbose = False

#parser_arguments:
def main():
    parser = ArgumentParser()

    parser.add_argument('AccessKeyId')
    parser.add_argument('AccessKeySecret')
    parser.add_argument('Domain')
    parser.add_argument('--add', metavar='<rr>')
    parser.add_argument('--delete', metavar='<rr>')
    parser.add_argument('--value', metavar='<value>')
    parser.add_argument('--type', metavar='<type>', default='A')
    parser.add_argument('--ttl', metavar='<ttl time>', default=600, type=int)
    parser.add_argument('--verbose', action='store_false')
        
    args = parser.parse_args()

    #print(args)
    
    R.verbose = args.verbose
    
    bs = client.AcsClient(args.AccessKeyId, args.AccessKeySecret,\
            'cn-hangzhou')
    
    records = query_record(bs, args.Domain)
    
    #add
    if args.add:
        if not args.value:
            args.value = get_def_inet()
        flag = is_exist(records, args.add)
        if flag:
            return update_record(bs, args.Domain, records[args.add][3],\
                args.value, args.add, args.type, args.ttl)
        else:
            return add_record(bs, args.Domain,\
                args.value, args.add, args.type, args.ttl)
    #delete
    if args.delete:
        flag = is_exist(records, args.delete)
        if flag:
            delete_record(bs, args.Domain, records[args.delete][3])
        else:
            parser.error('Recode: %s not exist!' % args.delete)
#delete
def delete_record(bs, domain, record_id):
    req = DeleteDomainRecordRequest()
    req.set_RecordId(record_id)
    
    try:
        js = json.loads(bs.do_action_with_exception(req).decode())
        #myprint('[*]delete record return:\n%s' % js)
    except Exception as e:
        myprint('[-]%s' % e)
    
def update_record(bs, domain, record_id, value, rr, rtype, ttl):
    req = UpdateDomainRecordRequest()
    req.set_RecordId(record_id)
    req.set_accept_format('json')
    req.set_RR(rr)
    req.set_Type(rtype)
    req.set_TTL(ttl)
    req.set_Value(value)
    
    try:
        js = json.loads(bs.do_action_with_exception(req).decode())
        #myprint('[*]update record return:\n%s' % js)
        myprint('[+]%s.%s -> %s;%s;%d' % (rr, domain, value, rtype, ttl))
    except Exception as e:
        myprint('[-]%s' % e)
  
def add_record(bs, domain, value, rr, rtype, ttl):
    req = AddDomainRecordRequest()
    req.set_DomainName(domain) 
    req.set_accept_format('json')
    req.set_RR(rr)
    req.set_Type(rtype)
    req.set_TTL(ttl)
    req.set_Value(value)
    
    try:
        js = json.loads(bs.do_action_with_exception(req).decode())
        #myprint('[*]add record return:\n%s' % js)
        myprint('[*]%8s.%s -> %-16s;  %-8s;%d' % (rr, domain, value, rtype, ttl))
    except Exception as e:
        myprint('[-]%s' % e)
    
#query record return a dictionary
def query_record(bs, domain):
    req = DescribeDomainRecordsRequest()
    req.set_accept_format('json')
    req.set_DomainName(domain)
    js = json.loads(bs.do_action_with_exception(req).decode())
    #myprint('[*]query record return:\n%s' % js)
    ret = {}
    for x in js['DomainRecords']['Record']:
        RR = x['RR']
        Type = x['Type']
        Value = x['Value']
        RecordId = x['RecordId']
        TTL = x['TTL']
        myprint('[*]%8s.%s -> %-16s;  %-8s;%d' % (RR, domain, Value, Type, TTL))
        ret[RR] = [Value, Type, TTL, RecordId]
    return ret

def myprint(msg):
    if R.verbose:
        print(msg)
        
def is_exist(records, rr):
    for i in records:
        if rr == i:
            return True
    return False

def get_def_inet():
    s = socket.socket()
    s.connect(('www.baidu.com',80))
    r = s.getsockname()[0]
    s.close()
    return r

if __name__=='__main__':
    main()
