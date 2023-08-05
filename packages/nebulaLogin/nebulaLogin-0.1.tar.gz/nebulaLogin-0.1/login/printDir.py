import ldap
import os
import json



def getHomeDir(userName):
	home_dir = os.path.join('/home',userName)
	walked = False
	for dir,subdirs,files in os.walk(home_dir):
		walked = True
		print('Found dir: %s' % dir)
		d = {'name':dir}	
		for subdir in subdirs:
			print ('\td %s'% subdir)
		for file in files:
			print ('\tf %s'% file)	
	if(not walked):
		print('get %s directory failed: permission denied' % userName)
		return None
	else:
		print('%s home directory walk finished' % userName)
		return path_to_dict(home_dir)



def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    else:
        d['type'] = "file"
    return d
