#!/usr/bin/env python  
#coding=utf-8
#  
# Generate a list of dnsmasq rules with ipset for gfwlist
#  
# Copyright (C) 2014 http://www.shuyz.com   
# Ref https://github.com/gfwlist/gfwlist   
 
import urllib2 
import re
import os
import datetime
import base64
import shutil
from my_config import EX_DOMAIN
 
mydnsip = '127.0.0.1'
mydnsport = '5353'
ipsetname = 'gfwlist'

# the url of gfwlist
baseurl = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'
# match comments/title/whitelist/ip address
comment_pattern = '^\!|\[|^@@|^\d+\.\d+\.\d+\.\d+'
domain_pattern = '([\w\-\_]+\.[\w\.\-\_]+)[\/\*]*' 
tmpfile = '/tmp/gfwlisttmp'
# do not write to router internal flash directly
outfile = './dnsmasq_list.conf'
#outfile = './dnsmasq_list.conf'
 
fs =  file(outfile, 'w')
 
print 'fetching list...'
content = urllib2.urlopen(baseurl, timeout=15).read().decode('base64')
 
# write the decoded content to file then read line by line
tfs = open(tmpfile, 'w')
tfs.write(content)
tfs.close()
tfs = open(tmpfile, 'r')
 
print 'page content fetched, analysis...'
 
# remember all blocked domains, in case of duplicate records
domainlist = []

 
for line in tfs.readlines():	
	if re.findall(comment_pattern, line):
		print 'this is a comment line: ' + line
		#fs.write('#' + line)
	else:
		domain = re.findall(domain_pattern, line)
		if domain:
			try:
				found = domainlist.index(domain[0])
				print domain[0] + ' exists.'
			except ValueError:
				print 'saving ' + domain[0]
				domainlist.append(domain[0])
				fs.write('server=/.%s/%s#%s\n'%(domain[0],mydnsip,mydnsport))
				fs.write('ipset=/.%s/%s\n'%(domain[0],ipsetname))
		else:
			print 'no valid domain in this line: ' + line
					
tfs.close()	

for each in EX_DOMAIN:
	fs.write('server=/%s/%s#%s\n'%(each,mydnsip,mydnsport))
	fs.write('ipset=/%s/%s\n'%(each,ipsetname))

print 'write extra domain done'

fs.close();
 
print 'done!'
