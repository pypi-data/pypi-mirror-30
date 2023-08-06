class settings:
	AUTH_LDAP_SERVER_URI='ldap://107.167.176.120'
	AUTH_LDAP_BIND_DN='cn=admin,dc=c,dc=majestic-lead-196504,dc=internal'
	AUTH_LDAP_BIND_PASSWORD='admin'
	base_dn='dc=c,dc=majestic-lead-196504,dc=internal'
        log_path = 'ldap.log'
	init_uid = 1400
	def __init__(self,uri=None,binddn=None,password=None,basedn=None,log_path=None,init_uid=None):
		if(uri!=None):
			self.AUTH_LDAP_SERVER_URI=uri
		if(binddn!=None):
			self.AUTH_LDAP_BIND_DN=binddn
		if(password!=None):
			self.AUTH_LDAP_BIND_PASSWORD=password
		if(basedn!=None):
			self.base_dn=basedn
		if(log_path != None):
			self.log_path=log_path
		if(init_uid != None):
                        self.init_uid = init_uid
