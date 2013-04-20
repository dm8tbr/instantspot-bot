#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
origin:
http://xmpppy.sourceforge.net/examples/bot.py
'''

from init_env import USERNAME, PASSWORD, SERVER, PORT
from init_env import WHITE_LIST_USERS

import pdb
import sys
import xmpp
import json
import urllib
import urllib2

from get_ip import get_ip

commands = {}
i18n = {
    'en': {}
    }
########################### user handlers start ##################################
i18n['en']['HELP'] = "This is instantspot bot.\nAvailable commands: %s"

def helpHandler(user, command, args, msg):
    lst = commands.keys()
    lst.sort()
    return "HELP", ',  '.join(lst)
commands['help'] = helpHandler

i18n['en']['EMPTY'] = "%s"
i18n['en']['NOW'] = '%s'
def nowHandler(user, command, args, msg):
    j = urllib2.urlopen('http://api.open-notify.org/iss-now/')
    j_obj = json.load(j)
    answer = 'Longitude: '+str(j_obj['iss_position']['latitude'])+' Latitude: '+str(j_obj['iss_position']['longitude'])
    return "NOW", '%s'%answer
commands['now'] = nowHandler

i18n['en']['WHEN'] = '%s'
def whenHandler(user, command, args, msg):
    # http://nominatim.openstreetmap.org/search?q=135+pilkington+avenue,+birmingham&format=json&polygon=0&addressdetails=1&limit=1&email=instantspot@ruecker.fi
        
    url = 'http://nominatim.openstreetmap.org/search?q='+urllib.quote_plus(str(args))+'&format=json&polygon=0&addressdetails=1&limit=1&email=instantspot@ruecker.fi'
    j = urllib2.urlopen(url)
    j_obj = json.load(j)
    #answer = 'Location request result (via OpenStreetMap and Nominatim): Latitude: '+str(j_obj['lat'])+' Longitude: '+str(j_obj['lon'])+' for: '+str(j_obj['display_name'])
    answer = str(url)
    return "WHEN", "%s"%answer
commands['when'] = whenHandler

i18n['en']['HOOK3'] = 'Responce 3: static string'
def hook3Handler(user, command, args, msg):
    return "HOOK3"*int(args)
commands['hook3'] = hook3Handler

def get_ip_hook(user, command, args, msg):
    # print '>>> get_ip_hook'
    # print 'user:', user
    # print 'command:', command
    # print 'args:', args
    # print 'msg:', msg
    for i in WHITE_LIST_USERS:
        if str(user).find(i) != -1:
            return str(get_ip()).strip()
        
commands['ip'] = get_ip_hook
########################### user handlers stop ###################################

############################ bot logic start #####################################
i18n['en']["UNKNOWN COMMAND"] = 'Unknown command "%s". Try "help"'
i18n['en']["UNKNOWN USER"] = "I do not know you. Register first."

def message_callback(conn, msg):
    text = msg.getBody()
    user = msg.getFrom()
    user.lang = 'en'      # dup
    if text is not None:
        if text.find(' ')+1: command, args = text.split(' ', 1)
        else: command, args = text, ''
        cmd = command.lower()

        if commands.has_key(cmd): reply = commands[cmd](user, command, args, msg)
        else: reply = ("UNKNOWN COMMAND", cmd)

        if type(reply) == type(()):
            key, args = reply
            if i18n[user.lang].has_key(key): pat = i18n[user.lang][key]
            elif i18n['en'].has_key(key): pat = i18n['en'][key]
            else: pat = "%s"
            if type(pat) == type(''): reply = pat%args
            else: reply = pat(**args)
        else:
            try: reply = i18n[user.lang][reply]
            except KeyError:
                try: reply = i18n['en'][reply]
                except KeyError: pass
        if reply: conn.send(xmpp.Message(msg.getFrom(), reply))

############################# bot logic stop #####################################

def StepOn(conn):
    try:
        conn.Process(1)
    except KeyboardInterrupt:
        return False
    return True

def GoOn(conn):
    while StepOn(conn):
        pass

def main():        
    if USERNAME == '' or PASSWORD == '' or SERVER == '':        
        print "Usage: bot.py username@server.net password"
        sys.exit(0)
        
    # jid = xmpp.JID(USERNAME)
    # user, server, password = jid.getNode(), jid.getDomain(), PASSWORD

    # conn = xmpp.Client(server)#, debug = [])
    conn = xmpp.Client(SERVER, debug = [])
    # conres = conn.connect()
    conres = conn.connect(server=(SERVER, PORT))
    if not conres:
        print "Unable to connect to server %s!" % SERVER
        sys.exit(1)

    if conres not in ('tls', 'ssl'):
        print "Warning: unable to estabilish secure connection - both TLS and SSL failed!"
    else:
        print 'Using secure connection - %s' % conres
        
    # authres = conn.auth(user, password)
    authres = conn.auth(USERNAME, PASSWORD)    
    if not authres:
        print "Unable to authorize on %s - check login/password." % SERVER
        sys.exit(1)
        
    if authres != 'sasl':
        print "Warning: unable to perform SASL auth os %s. Old authentication method used!" % SERVER
        
    conn.RegisterHandler('message', message_callback)
    conn.sendInitPresence()
    print "Bot started."
    
    GoOn(conn)

if __name__ == '__main__':
    main()
