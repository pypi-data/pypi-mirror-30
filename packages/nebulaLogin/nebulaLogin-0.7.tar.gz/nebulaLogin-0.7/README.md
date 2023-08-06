# nebulaLogin Installation guide

  - pre-dependencies
  - install nebulaLogin
  - test

## pre-dependencies
#
#### Install pip
#
  ```python
$  wget https://bootstrap.pypa.io/get-pip.py
$  python get-pip.py
  ```
#### Install gcc
 for ubuntu & debian
```python
$ sudo apt install gcc 
```
for CentOS
```python
$ sudo yum install gcc 
```
  
#### Install python-ldap
This package access ldap server by  [python-ldap] and python-ldap will be automatically installed.But before that,some dev package are needed

for Ubuntu & Debian
```
$ sudo apt install libsasl2-dev python-dev libldap2-dev libssl-dev
```
for CentOS:
```
$ sudo yum install python-devel openldap-devel
```


## Install nebulaLogin
#
```
$ sudo pip install nebulaLogin
```

## Test login
#
```
$ python
```
```
>>> from login import login
>>> login.LDAPlogin('test','test')
```


# 2. APIs

#### class  ldapTool2.LDAPTool(object) methods:

```
ldap_search_dn(self, value=None, value_type='uid')
ldap_add_user(self, cn, mail, username, password)
check_user_belong_to_group(self, uid, group_cn='kevindwliu')
ldap_get_user(self, uid=None)
```

#### login package methods:

```
LDAPlogin(userName,password)
```



[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
[python-ldap]: <https://www.python-ldap.org>
