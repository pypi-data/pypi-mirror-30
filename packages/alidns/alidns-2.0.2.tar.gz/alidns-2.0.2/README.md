## alidns
#### Aliyun-DNS update tool.
### How to install :
```bash
 pip install alidns
```
### Help : 
```bash
alidns -h

Aliyun DNS Record Update Tools.

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
```
### Changes : 
#### v2.0.0
* use docopt module.
#### v2.0.1
* fix update error.