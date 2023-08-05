#!/usr/bin/env python

import socket
if 'guestshell' in socket.gethostname():
	import cli
import logging

log = logging.getLogger('dmvpn')
log.setLevel(logging.INFO)

def cmd_execute(command):
	'''

	Note: for some reason initial pull/show always results in broken or non existent result. Hence execute show commands TWICE always.
	'''
	if 'guestshell' in socket.gethostname():
		output = cli.execute(command)
		#output = cli.execute(command)
	else:
		output = command
	#output = commands
	log.info(output)
	return output


def cmd_configure(config):
	log.info(config)
	if 'guestshell' in socket.gethostname():
		output = cli.configure(config)
	else:
		output = config
	log.info(output)
	return output

