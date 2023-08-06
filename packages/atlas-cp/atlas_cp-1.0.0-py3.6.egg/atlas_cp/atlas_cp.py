#!/usr/bin/env python3

import requests
import os
import time
import stat
import sys
import urllib3
import argparse
import readline
import json
from ldap3 import Server, Connection, ALL_ATTRIBUTES, SUBTREE, ALL_OPERATIONAL_ATTRIBUTES
from getpass import getpass

CP_USERS_ADGROUP = "CN=atlasCrashPlanUsers,OU=Groups,OU=CrashPlan,OU=Infrastructure,OU=ATLAS,OU=LAS,OU=Urbana,DC=ad,DC=uillinois,DC=edu"
CP_MASTER = "https://cpmaster.lis.illinois.edu:4285"

def get_user_passwd():
    user = input("username: ")
    passwd = getpass("password: ")
    return (user, passwd)

def get_token(server, auth):
    path = "{}/api/authToken".format(server)
    r = requests.post(path, auth=auth, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json() 
    else:
        print("Error {}".format(r.status_code))

class CPApi:
    def __init__(self, server, authtoken, auth):
        self.server = server
        self.sess = requests.session()
        self.sess.verify = False
        self.sess.headers.update({'Authorization': authtoken})
        self.loadorgs()

        ldapserver = Server('ad.uillinois.edu')
        self.ldap = Connection(ldapserver, user="uofi\\{}".format(auth[0]), password=auth[1], auto_bind=None)
        self.ldap.open()
        self.ldap.start_tls()
        if not self.ldap.bind():
            print("Error binding to AD: {}".format(self.ldap.result))
            sys.exit(1)

        self.loadadgroup()

    def apicall(self, req, method="get", data=False):
        path = "{}/api/{}".format(self.server, req)
        if method == "get":
            r = self.sess.get(path)
        elif method == "post":
            r = self.sess.post(path, data=json.dumps(data))   

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            print("Error communicating with CP server")
            return False

    def loadorgs(self):
        self.orgs = self.apicall("Org")['data']['orgs']


    def loadadgroup(self, adgroup=CP_USERS_ADGROUP):
        self.adgroup = []
        search_filter = "(&(objectclass=person)(memberOf:={}))".format(adgroup)
        self.ldap.search('dc=ad,dc=uillinois,dc=edu', search_filter, search_scope=SUBTREE, attributes=['sAMAccountName'])
        for entry in self.ldap.entries:
            self.adgroup.append(entry['sAMAccountName'])

    def find_user(self, netid):
        req = "User?q={}".format(netid)
        users = self.apicall(req)['data']
        print("{:10} | {:25} | {:10} | {:3} | {:8}".format("username", "name", "org", "AD?", "Active?"))
        print("-" * 80)

        for user in users['users']:
            active = "Y" if user['active'] else "N"
            inad = "Y" if user['username'] in self.adgroup else "N"
            name = "{} {}".format(user['firstName'], user['lastName'])
            print("{:10} | {:25} | {:10} | {:3} | {:3}".format(user['username'], name, user['orgName'], inad, active))

    def find_specific_user(self, netid):
        req = "User?q={}".format(netid)
        users = self.apicall(req)['data']
        for user in users['users']:
            if user['username'] == netid:
                return user
        return False

    def find_org(self, s):
        for org in self.orgs:
            if s.lower() in org['orgName'].lower():
                print(org['orgName'])
                

    def find_specific_org(self, s):
        for org in self.orgs:
            if s.lower() == org['orgName'].lower():
                return org
        return False

    def add_user(self, username, orgname, adgroup=CP_USERS_ADGROUP):
        org = self.find_specific_org(orgname)
        user_exists = self.find_specific_user(username)

        if user_exists != False:
            print("User already exists")
            return True
        
        # Find the user DN
        search_filter = "(&(objectclass=person)(sAMAccountName={}))".format(username)
        self.ldap.search('dc=ad,dc=uillinois,dc=edu', search_filter, attributes=['sn', 'givenName', 'mail'])

        entries = self.ldap.entries
        if len(entries) != 1:
            print("User not found")
            return False

        user_dn = entries[0].entry_dn
        user = {
            "orgUid" : org['orgUid'],
            "username": username,
            "firstName": entries[0]['givenName'].value,
            "lastName": entries[0]['sn'].value,
            "email": entries[0]['mail'].value
        }

        try:
            res = self.ldap.extend.microsoft.add_members_to_groups(user_dn, adgroup)
            if not res:
                print("Error adding user to AD group")
            print("Added {} to our AD group".format(username))
        except:
            print("Error adding user to AD group")
            return False

        print("Sleeping for 5 seconds")
        time.sleep(5)

        self.loadadgroup()

        ret = self.apicall("User", method="post", data=user)
        if ret != False:
            print("User added to CP with userUid {}".format(ret['data']['userUid']))
            return True
        else:
            print("Error occurred")
            return False

def main():
    server = CP_MASTER
    urllib3.disable_warnings()
    auth = get_user_passwd()
    token = get_token(server, auth)
    authtoken = "token {}-{}".format(token['data'][0], token['data'][1])

    cp = CPApi(server, authtoken, auth)

    parser = argparse.ArgumentParser(prog='')
    main_subparsers = parser.add_subparsers(dest='command')

    find_parser = main_subparsers.add_parser('find')
    find_subparsers = find_parser.add_subparsers(dest='subcommand')
    find_user_parser = find_subparsers.add_parser('user')
    find_user_parser.add_argument('name')
    find_org_parser = find_subparsers.add_parser('org')
    find_org_parser.add_argument('name')

    add_parser = main_subparsers.add_parser('add')
    add_subparsers = add_parser.add_subparsers(dest='subcommand')
    add_user_parser = add_subparsers.add_parser('user')
    add_user_parser.add_argument('username')
    add_user_parser.add_argument('org')

    readline.parse_and_bind("")
    while True:
        action = input("cp> ")
        try:
            args = parser.parse_args(action.split(' '))
        except argparse.ArgumentError as err:
            print(err)
            continue
        except SystemExit:
            continue

        if args.command == 'find':
            method = getattr(cp, "{}_{}".format(args.command, args.subcommand))
            method(args.name)
        elif args.command == 'add':
            method = getattr(cp, "{}_{}".format(args.command, args.subcommand))
            method(args.username, args.org)
