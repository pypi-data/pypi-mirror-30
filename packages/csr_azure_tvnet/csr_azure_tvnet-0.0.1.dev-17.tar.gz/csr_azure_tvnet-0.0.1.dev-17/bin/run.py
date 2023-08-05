#!/usr/bin/env python

'''
Cisco Copyright 2018
Author: Vamsi Kalapala <vakalapa@cisco.com>

FILENAME: RUN.PY


'''

import os
import time
import parse
import socket
import random
import argparse
import getmetadata
from configs import *
from shutil import copyfile
from datetime import datetime
from azurestorage import azsto
from dmvpn import configure_transit_vnet,get_interfaces_ips
import logging


def setup_directory(tvnet_home='/home/guestshell/azure_tvnet'):
	'''
	This function will help with setting up directory structure.

	'''
	folder_list = ['logs', 'data','bin']
	if not os.path.exists(tvnet_home):
		os.makedirs(tvnet_home)
	for folder in folder_list:
		folder_path = os.path.join(tvnet_home, folder)
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
	return tvnet_home

def copy_custom_data_file(file, tvnet_home):
	dest = os.path.join(tvnet_home, 'customdata.txt')
	if not os.path.exists(dest):
		if os.path.exists(file):
			copyfile(file,dest)
		else:
			log.error('FATAL ERROR: No custom data file found!')
			return False
	return dest

def setup_logging(tvnet_home):
	log = logging.getLogger('dmvpn')
	folder = 'logs'
	logfile_name = 'tvnetlog_' + str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')) + '.txt'
	hdlr = logging.FileHandler(os.path.join(tvnet_home,folder,logfile_name))
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	log.addHandler(hdlr) 
	log.setLevel(logging.INFO)

def main(args):
	'''
	MAIN function starts all the necessary stuff

	Main function involves taking care of:
		- Creating a local copy of the Custom Data file
		- Parsing the Custom data and creating data structure


	'''
	log = logging.getLogger('dmvpn')
	log.setLevel(logging.INFO)

	new_cd_file = copy_custom_data_file(args.decoded, tvnet_home)
	if not new_cd_file:
		return False

	section_dict = parse.parse_decoded_custom_data(new_cd_file)
	if not section_dict:
		log.error('FATAL ERROR: There are no details found in customdata file')
		print('FATAL ERROR: There are no details found in customdata file')
		return False
	
	try:
		storage_object = azsto(section_dict['strgacctname'], section_dict['strgacckey'])
		section_dict['storage_object']  = storage_object
	except KeyError:
		log.error('FATAL ERROR: strgacctname or strgacckey are not found!')
		print('FATAL ERROR: strgacctname or strgacckey are not found!')
		return False

	section_dict = parse.setup_file_dict(section_dict)

	if 'spoke' in section_dict['role']:
		section_dict = parse.get_all_files(section_dict)
	'''
	# This Below section is being commented out.
	# Uncommenting below part will enable the HUBs to check for existing params 
	# in storage accoutn and prioritize them over custam data inputs.
	elif 'hub' in section_dict['role']:
		section_dict = parse.get_all_files(section_dict, ['dmvpn'])
	'''

	section_dict = parse.setup_default_dict(section_dict)

	role = section_dict['role']
	tunnel_network = section_dict['DMVPNTunnelIpCidr']
	if 'hub' in role.lower():
		log.info('[INFO] Configuring router as {}'.format(role))
		hub_dict = {}
		hub_dict['pip'] = getmetadata.get_pip()
		if '1' in role:
			tunn_addr = tunnel_network.network_address + 1
			hub_dict['nbma'] = str(tunn_addr)
			section_dict['hub-1'] = hub_dict
			section_dict['spoke'] = {'count' :  0 }
		else:
			tunn_addr = tunnel_network.network_address + 2
			hub_dict['nbma'] = str(tunn_addr)
			section_dict['hub-2'] = hub_dict
	elif role.lower() == 'spoke':
		log.info('[INFO] Configuring router as SPOKE')
		try:
			dmvpn_address_count = tunnel_network.num_addresses
			spoke_vmid = getmetadata.get_vmid()
			spoke_pip = getmetadata.get_pip()
			random.seed(spoke_vmid)
			rand_tunn_offset = random.randint(10, dmvpn_address_count)
			section_dict['spoke']['count'] = int(section_dict['spoke']['count'] )
			section_dict['spoke']['count'] += 1
			tunn_addr = tunnel_network.network_address + rand_tunn_offset
			section_dict['spoke'][spoke_vmid] = {'pip' : str(spoke_pip), 'tunnel_address' : str(tunn_addr)}
		except KeyError:
			log.info('[ERROR] Spoke count is not found in spoke file contents.')
			return None
	else:
		log.info('[ERROR] Unrecognised role is assigned to the router!')

	parse.write_all_files(section_dict)
	section_dict = configure_transit_vnet(section_dict, tunn_addr)
	cmd_execute("send log [INFO] [AzureTransitVNET] Success. Configured all the required IOS configs.".format(role))



if __name__ == '__main__': # pragma: no cover
	tvnet_home = setup_directory()
	setup_logging(tvnet_home)
	parser = argparse.ArgumentParser()
	parser.add_argument('-d','--decoded', type=str, default="sampledecodedCustomData", help='File location for the decoded custom data')
	args = parser.parse_args()
	main(args)