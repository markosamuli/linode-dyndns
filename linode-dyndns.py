#!/usr/bin/python
"""
linode-dns.py
Author: Michael Shepanski
Date: Jan 17, 2010

linode-dyndns.py
Updates: Matthew Schick
A script to update a DNS record on Linode to your external IP.

References:
  http://atxconsulting.com/content/linode-api-bindings
  https://github.com/tjfontaine/linode-python/
"""
import pycurl
import re
from linode import api
from StringIO import StringIO

APIKEY = 'APIKEY'
DOMAIN = 'DOMAIN'
RECORD = 'RECORD'

def get_external_ip():
    """ Return the current external IP. """
        
    html = StringIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, "http://automation.whatismyip.com/n09230945.asp")
    curl.setopt(curl.WRITEFUNCTION, html.write)
    curl.perform()
    curl.close()
    external = re.findall('[0-9.]+', html.getvalue())[0]
    return external

def set_dns_target(utarget, udomain=DOMAIN, urecord=RECORD):
    """ Update the domain's DNS record with the specified target. """
    linode = api.Api(APIKEY)
    for domain in linode.domain_list():
        if domain['DOMAIN'] == udomain:
            # Check the DNS Entry already exists
            for record in linode.domain_resource_list(domainid=domain['DOMAINID']):
                if record['NAME'] == urecord:
                    if record['TARGET'] == utarget:
                        # DNS Entry Already at the correct value
                        print "Entry '%s:%s' already set to '%s'." % (udomain, urecord, utarget)
                        return record['RESOURCEID']
                    else:
                        # DNS Entry found; Update it
                        print "Updating entry '%s:%s' target to '%s'." % (udomain, urecord, utarget)
                        return linode.domain_resource_update(domainid=domain['DOMAINID'],
                            resourceid=record['RESOURCEID'], target=utarget)
            # DNS Entry not found; Create it
            print "Creating entry '%s:%s' target as '%s'." % (udomain, urecord, utarget)
            return linode.domain_resource_create(domainid=domain['DOMAINID'],
                name=urecord, type='A', target=utarget, ttl_sec=300)
            print "Error: Domain %s not found." % udomain

if __name__ == '__main__':
    external_ip = get_external_ip()
    if external_ip:
        #print "set_dns_target(%s, %s, %s)" % (external_ip, DOMAIN, RECORD)
        set_dns_target(external_ip, DOMAIN, RECORD)
