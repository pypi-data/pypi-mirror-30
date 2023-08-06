# -*- coding:utf-8 -*-
import ldap
import ldap.modlist as modlist

import pdb
import logging
#logger = logging.getLogger()
import sys
reload(sys)
sys.setdefaultencoding('utf8')


from ldapAdmin import settings
LDAP_URI = settings.AUTH_LDAP_SERVER_URI
LDAP_USER = settings.AUTH_LDAP_BIND_DN
LDAP_PASS = settings.AUTH_LDAP_BIND_PASSWORD
BASE_DN = settings.base_dn
LOG_PATH = settings.log_path
logging.basicConfig(filename=LOG_PATH,level=logging.ERROR)

class LDAPTool(object):
    def __init__(self,
                 ldap_uri=None,
                 base_dn=None,
                 user=None,
                 password=None):
       
#        initialize
#        :param ldap_uri: ldap_uri
#        :param base_dn:base dn
#        :param user: default user
#        :param password: default password
#        :return:
        
        if not ldap_uri:
            ldap_uri = LDAP_URI
        if not base_dn:
            self.base_dn = BASE_DN
        if not user:
            self.admin_user = LDAP_USER
        if not password:
            self.admin_password = LDAP_PASS
        try:
            self.ldapconn = ldap.initialize(ldap_uri)  # open() for older versions
            self.ldapconn.simple_bind(self.admin_user, self.admin_password)
        except ldap.LDAPError, e:
            logging.error('ldap conn failed，because: %s' % str(e))

    def ldap_search_dn(self, value=None, value_type='uid'):
        """
        :param value: uid or group cn
        :param value_type: user uid|cn
        :return: search result,format is [(dn1,{user1 info}),(dn1,{user1 info}),(dn1,{user1 info}) ... ]
        """
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        if value_type == 'cn':
            searchFilter = "cn=" + value
        else:
            searchFilter = "uid=" + value
        try:
            ldap_result_id = obj.search(
                base=self.base_dn,
                scope=searchScope,
                filterstr=searchFilter,
                attrlist=retrieveAttributes
            )
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                return result_data
            else:
                return None
        except ldap.LDAPError, e:
            logging.error('ldap search %s failed, because: %s' % (value, str(e)))

    def ldap_get_user(self, uid=None):
        """
        :param uid:
        :return: {‘uid’:'zhangsan','mail':'zhangsan@xxx.com','cn':'张三'}
        """
        result = None
        try:
            search = self.ldap_search_dn(value=uid, value_type=uid)
            if search is None:
                raise ldap.LDAPError('corresponding id not found')
            for user in search:
                if user[1]['uid'][0] == uid:
#                    pdb.set_trace()
		    result = {
                        'uid': uid,
			'uidNumber': int(user[1]['uidNumber'][0]),
			'gidNumber': int(user[1]['gidNumber'][0]),
                        #'mail': user[1]['mail'][0] if  user[1]['mail'] !=None else '',
                        'cn': user[1]['cn'][0],
                    }
		    if(user[1].has_key('mail')):
			result['mail'] = user[1]['mail'][0]
		    
        except Exception, e:
            logging.error('get user %s failed，because: %s' % (uid, str(e)))
        return result

    def __ldap_getgid(self, cn="kevindwliu"):
        """
        get cn gid
        :param cn: group cn
        :return: cn gidNumber
        """
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "cn=" + cn
        try:
            ldap_result_id = obj.search(
                base="ou=groups,%s" % self.base_dn,
                scope=searchScope,
                filterstr=searchFilter,
                attrlist=retrieveAttributes
            )
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                return result_data[0][1].get('gidNumber')[0]
            else:
                return None
        except ldap.LDAPError, e:
            logging.error('get gid failed，because: %s' % str(e))

    def __get_max_uidNumber(self):
        """ 
        :param: None
        :return: max uidNumber
        """
        f = None
	try:
	    f = open('max_uid.txt','r')
	    last_max = int(f.read())
	    return last_max # if max uid already in max_uid.txt,return it
	except IOError,e:
	    print e
	    	    
	finally:
	    if f:
		f.close()

        #max uid not in max_uid.txt,means it will be the first user added
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ['uidNumber']
        searchFilter = "uid=*"
	#pdb.set_trace()
        try:
            ldap_result = obj.search(
                base="ou=people,%s" % self.base_dn,
                scope=searchScope,
                filterstr=searchFilter,
                attrlist=retrieveAttributes
            )
            #result_set = [i]
            result = ldapAdmin.init_uid
	    while True:
                result_type, result_data = obj.result(ldap_result, 0)
                if not result_data:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        tmpuid = int(result_data[0][1].get('uidNumber')[0])
			if(tmpuid>result):		    
	    		    result = tmpuid

            f = None 
	    try:
		f = open('max_uid.txt','w')
		f.write(str(result))
	    except Exception,e:
		print e
	    finally:
		if f:
		    f.close()

 	    return result
        except ldap.LDAPError, e:
            logging.error('get max uid failed，because: %s' % str(e))

    def ldap_add_user(self, cn, mail, username, password):
        """
        add ldap user
        :param cn, mail, username, password
        :return: True/None
        """
        result = None
        try:
            #pdb.set_trace()
	    obj = self.ldapconn
            obj.protocal_version = ldap.VERSION3

            addDN = "uid=%s,ou=people,%s" % (username, BASE_DN)
            attrs = {}
            attrs['objectclass'] = ['top', 'person', 'inetOrgPerson', 'posixAccount', 'organizationalPerson']
            attrs['cn'] = str(cn)
            attrs['homeDirectory'] = str('/home/%s' % username)
            attrs['loginShell'] = '/bin/bash'
            attrs['mail'] = str(mail)
            attrs['sn'] = str(username)
            attrs['uid'] = str(username)
            attrs['userPassword'] = str(password)
            attrs['uidNumber'] = str(self.__get_max_uidNumber()+1)
            attrs['gidNumber'] = str(1001)#self.__ldap_getgid(cn='kevindwliu')
            ldif = ldap.modlist.addModlist(attrs)
#           pdb.set_trace()
	    obj.add_s(addDN, ldif)
            obj.unbind_s()
            result = True
	    
	    print('add user success!')
            f = None
            try:
		f = open('max_uid.txt','w')
		f.write(attrs['uidNumber'])
	    except IOError,e:
		print e
	    finally:
		if f:
		    f.close()
	except ldap.LDAPError, e:
            print('add user failed:%s'% str(e))
	    logging.error("add user %s failed，because: %s" % (username, str(e)))
        return result

    def check_user_belong_to_group(self, uid, group_cn='kevindwliu'):
        """
        :param uid: uid , Ex: 'admin'
        :param group_cn:cn , Ex: ''
        :return: True|None
        """
        result = None
        try:
            search = self.ldap_search_dn(value=group_cn, value_type='cn')
            if search is None:
                raise ldap.LDAPError('no result for id')

            member_list = search[0][1].get('memberUid', [])
            if uid in member_list:
                result = True
        except ldap.LDAPError, e:
            logging.error('get user %s and %s failed，because: %s' % (uid, group_cn, str(e)))
        return result

    def check_user_status(self, uid):
        """
        :param uid: uid
        :return: 200: user ok
                 404: user does not exists
                 403: user forbidden
        """
        result = 404
        try:
            target_cn = self.ldap_get_user(uid=uid)
            if target_cn is None: 
                result = 404
                logging.debug("%s uid no result" % uid)
            else:
                if self.check_user_belong_to_group(uid=uid, group_cn='forbidden'):
                    result = 403
                else:
                    result = 200
        except ldap.LDAPError, e:
            logging.error("check user %s status failed,because %s" % (uid, str(e)))
        return result

    def ldap_update_password(self, uid, new_password):
        """
        
        :param uid: uid，password
        :return: True|None
        """
        result = None
        try:
            obj = self.ldapconn
            obj.protocal_version = ldap.VERSION3
            modifyDN = "uid=%s,ou=People,%s" % (uid, BASE_DN)
            obj.modify_s(modifyDN, [(ldap.MOD_REPLACE, 'userPassword', [str(new_password)])])
            obj.unbind_s()
            result = True
        except ldap.LDAPError, e:
            logging.error("%s reset password failed，because: %s" % (uid, str(e)))
        return result
