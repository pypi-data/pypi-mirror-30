'''Aliyun DNS Record Update Tools.

Usage:
 alidns config  <key> <key-secret> <domain>
 alidns clean
 alidns list
 alidns add     [-r=<record>] [-v=<ip>] [-t=<type>] [--ttl=<ttl>]
 alidns remove  <record>

Commands:
 config         Config Key key-secret and domain.
 clean          Clean config.
 
Arguments:
 -r=<record>    Host record.
 -v=<ip>        Host ip.
 -t=<type>      Record type.
 --ttl=<ttl>    Record ttl.

Examples:
 alidns config 12341234 12341234 forks.club
 alidns add -r @ -v 127.0.0.1 -t A --ttl 600
'''

from aliyunsdkcore import client
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest       import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DeleteDomainRecordRequest    import DeleteDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest    import UpdateDomainRecordRequest

from docopt import docopt
import json
import socket
import os

class Alidns(object):
    def __init__(self, key, key_secret, domain):
        '''init'''
        self.__domain = domain
        self.__bs = client.AcsClient(key, key_secret,'cn-hangzhou')
        self.__print = ''
        self.__records = self.query()
                                      
    def query(self):
        '''Query all host records.'''
        req = DescribeDomainRecordsRequest()
        req.set_accept_format('json')
        req.set_DomainName(self.__domain)
        js = json.loads(self.__bs.do_action_with_exception(req).decode())
        ret = {}
        strs = ''
        for x in js['DomainRecords']['Record']:
            RR = x['RR']
            Type = x['Type']
            Value = x['Value']
            RecordId = x['RecordId']
            TTL = x['TTL']
            strs = strs + '[*]%8s.%s -> %-16s;  %-8s;%d\n' % (RR, self.__domain, Value, Type, TTL)
            ret[RR] = [Value, Type, TTL, RecordId]
        self.__print = strs
        return ret
        
    def list(self, update=True):
        '''Print query results.'''
        if update:
            self.query()
        print(self.__print)
        
    def __is_exist(self, r):
        '''Record exist?'''
        for i in self.__records:
            if r == i:
                return True
        return False
        
    def __get_ip(self):
        '''Get default interface ip address(v4)'''
        s = socket.socket()
        s.connect(('baidu.com',80))
        r = s.getsockname()[0]
        s.close()
        return r
        
    def __update_record(self, record_id, record, value, record_type, ttl):
        '''Update record.'''
        req = UpdateDomainRecordRequest()
        req.set_RecordId(record_id)
        req.set_accept_format('json')
        req.set_RR(record)
        req.set_Type(record_type)
        req.set_TTL(ttl)
        req.set_Value(value)
        js = json.loads(self.__bs.do_action_with_exception(req).decode())
        print('[+]%s.%s -> %s;%s;%d' % (record, self.__domain, value, record_type, ttl))
        
    def __add_record(self, record, value, record_type, ttl):
        '''Add record.'''
        req = AddDomainRecordRequest()
        req.set_DomainName(self.__domain)
        req.set_accept_format('json')
        req.set_RR(record)
        req.set_Type(record_type)
        req.set_TTL(ttl)
        req.set_Value(value)
        js = json.loads(self.__bs.do_action_with_exception(req).decode())
        print('[+]%8s.%s -> %-16s;  %-8s;%s' % (record, self.__domain, value, record_type, ttl))
                
    def add(self, record, value, record_type, ttl):
        '''Add record'''
        if not record:
            record = '@'
        if self.__is_exist(record):
            if not value:
                if self.__records[record][1] == 'A':
                    value = self.__get_ip()
                else:
                    value = self.__records[record][0] 
            if not record_type:
                record_type = self.__records[record][1]    
            if not ttl:
                ttl = self.__records[record][2]
            else:
                ttl = int(ttl)
                
            if self.__records[record][0] != value:
                self.__update_record(self.__records[record][3], record, value, record_type, ttl)
            elif self.__records[record][1] != record_type:
                self.__update_record(self.__records[record][3], record, value, record_type, ttl)
            elif self.__records[record][2] != ttl:
                self.__update_record(self.__records[record][3], record, value, record_type, ttl)
            else:
                pass
        else:
            if not value:
                value = self.__get_ip()
            if not record_type:
                record_type = 'A'
            if not ttl:
                ttl = 600
            self.__add_record(record, value, record_type, ttl)
        self.list()
        
    def __remove_record(self, record_id):
        '''Remove record'''
        req = DeleteDomainRecordRequest()
        req.set_RecordId(record_id)
        js = json.loads(self.__bs.do_action_with_exception(req).decode())
            
    def remove(self, record):
        '''Remove record'''
        if self.__is_exist(record):
            self.__remove_record(self.__records[record][3])
        else:
            print('[-]Record: {} is not existence.'.format(record))
        self.list()
    
def main():
    '''Parse arguments with docopt.'''
    args = docopt(__doc__)
    #print(args)
    if args['config'] == True:
        with open(get_home_file(), 'w') as f:
            f.write('{} {} {}'.format(args['<key>'], args['<key-secret>'], args['<domain>']))
        Alidns(args['<key>'], args['<key-secret>'], args['<domain>']).list()            
    elif args['clean'] == True:
        os.remove(get_home_file())
    else:
        if os.path.exists(get_home_file()):
            key = ''
            key_secret = ''
            domain = ''
            with open(get_home_file(),'r') as f:
                s = f.read().split()
                key = s[0]
                key_secret = s[1]
                domain = s[2]
            ali = Alidns(key, key_secret, domain)
            if args['list'] == True:
                ali.list()
            elif args['add'] == True:
                ali.add(args['-r'], args['-v'], args['-t'], args['--ttl'])
            elif args['remove'] == True:
                ali.remove(args['<record>'])
            else:
                print(__doc__)
        else:
            print('[-]Need config,use [alidns config] command.')
        
def get_home_file():
    """Get home file path."""
    parent = None
    if os.name == 'nt':
        parent = os.environ['USERPROFILE'] + '\\alidns\\'
    else:
        parent = os.environ['HOME'] + '/alidns/'
    if not os.path.isdir(parent):
        os.mkdir(parent)
    return parent + 'alidns'
        
if __name__=='__main__':
    main()