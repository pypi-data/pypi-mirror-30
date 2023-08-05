



import ldap
import pdb
import printDir
import os
import ldapTool2
'''first get dn ,then verify username and password
'''
from ldapAdmin import settings
ldappath = settings.AUTH_LDAP_SERVER_URI
ldapadmin = settings.AUTH_LDAP_BIND_DN
ldappasswd = settings.AUTH_LDAP_BIND_PASSWORD
baseDn = settings.base_dn

#ldappath = 'ldap://10.140.0.5'
#baseDn = 'dc=c,dc=majestic-lead-196504,dc=internal'
#ldapadmin = 'admin'
#ldappasswd = 'admin'


def LDAPlogin(userName,password):
	try:
		if(password == ''):
			print "password is empty"
			return
		
		dn = getDn(userName)
		if(dn == ''):
			raise Exception('user does not exits')
			#print "user does not exits"
			#return 
		ldap_server = ldap.initialize(ldappath)
		print ldap_server.simple_bind_s(dn,password)
		print "%s login Ok" % userName
#		flag = raw_input("get %s 's home directory? y/n: " % userName)
#		if(flag=='y'):
#			jsonResult = printDir.getHomeDir(userName)
#			print JSON.stringify(jsonResult,null,' ')
#			#print ('cannot access!' if dir==None else dir)
	except Exception,e:
		print "%s login failed: %s" % (userName,e)
		return
	
	if(not os.path.exists('/home/%s' % userName)):
		try:
			tool = ldapTool2.LDAPTool()
			result = tool.ldap_get_user(userName)
			os.makedirs('/home/%s' % userName)
			os.chown('/home/%s' % userName,result['uidNumber'],result['gidNumber'])
		except Exception,e:
			print('make home dir failed,%s'% str(e))

	jsonResult = printDir.getHomeDir(userName)
	if(jsonResult is None):
		print("get json failed")
		return
	flag = raw_input("get %s 's home directory in json? y/n: " % userName)
        if(flag=='y'):
                print jsonResult
                #print ('cannot access!' if dir==None else dir)




def getDn(userName,trynum=30):
	i = 0
	isFound = 0
	foundResult = ''
	print('getting Dn...')
	#pdb.set_trace()
	while(i<trynum):
		isfound,foundResult = _validateLDAPUser(userName)
		if(isfound):
			break
		i+=1
	#print('Dn is %s' % foundResult)
	return foundResult	


def _validateLDAPUser(user): #return isfound and foundresult
	try:
		l = ldap.initialize(ldappath)
		l.protocol_version = ldap.VERSION3
		l.simple_bind(ldapadmin,ldappasswd)
		
		searchScope = ldap.SCOPE_SUBTREE
		searchFiltername = 'uid'
		retrieveAttributes = None
		searchFilter = '(' + searchFiltername + '=' + user + ')'
		#pdb.set_trace()		
		ldap_result_id = l.search(baseDn,searchScope,searchFilter,retrieveAttributes)
		result_type,result_data = l.result(ldap_result_id,1)
		if(len(result_data) != 0):
			r_a,r_b = result_data[0]
	        	return 1, r_a
		else:
			return 0,''
	
	except ldap.LDAPError,e:
		print e
		return 0,''
	
	finally:
		l.unbind()
		del l
