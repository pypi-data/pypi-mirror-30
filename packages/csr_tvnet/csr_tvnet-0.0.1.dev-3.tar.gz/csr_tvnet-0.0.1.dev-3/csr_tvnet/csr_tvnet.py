#!/usr/bin/env python
from cloud.cloud_api import cloudapi
import time
import random
import string
import logging
import ipaddress
from shutil import copyfile
import os
from configs import *
from datetime import datetime

try:
    import cli
except IOError as e:
    raise IOError("We are not running with cli")


log = logging.getLogger('csr_tvnet')
tvnet_home = '/home/guestshell/csr_tvnet'


def setup_directory(directory):
    '''
    This function will help with setting up directory structure.

    '''
    folder_list = ['logs', 'data', 'bin']
    if not os.path.exists(directory):
        os.makedirs(directory)
    for folder in folder_list:
        folder_path = os.path.join(directory, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


def copy_custom_data_file(file):
    dest = os.path.join(tvnet_home, 'customdata.txt')
    if not os.path.exists(dest):
        if os.path.exists(file):
            copyfile(file, dest)
        else:
            log.error('FATAL ERROR: No custom data file found!')
            return False
    return dest


def setup_logging(directory):
    log = logging.getLogger('csr_tvnet')
    folder = 'logs'
    logfile_name = 'tvnetlog_' + \
        str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')) + '.txt'
    hdlr = logging.FileHandler(os.path.join(directory, folder, logfile_name))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.INFO)


class csr_transit():
    def __init__(self, customDataFileName):
        try:
            import cli
            self.guestshell = True

        except IOError as e:
            self.guestshell = False

        self.section_dict = {}
        setup_directory(tvnet_home)
        setup_logging('csr_tvnet')
        self.cd_file = copy_custom_data_file(customDataFileName)
        if not self.cd_file:
            raise IOError("Failed to load Custom Data File")

        if not self.parse_decoded_custom_data():
            raise IOError("Failed to parse Custom Data File")

        self.cloud = cloudapi(
            self.section_dict['strgacctname'],
            self.section_dict['strgacckey'])

        self.setup_file_dict()
        self.get_all_files()
        self.setup_default_dict()

    def cmd_execute(self, command):
        '''

        Note: for some reason initial pull/show always results in broken or non existent result. Hence execute show commands TWICE always.
        '''
        if self.guestshell:
            output = cli.execute(command)
        else:
            output = command
        # output = commands
        log.info(output)
        return output

    def cmd_configure(self, config):
        log.info(config)
        if self.guestshell:
            output = cli.configure(config)
        else:
            output = config
        log.info(output)
        return output

    def configure_tunnel(self, tunn_addr):
        cmd = ''
        role = self.section_dict['role'].lower()

        if 'hub' in role:
            if 'eigrp' in self.section_dict['dmvpn']["RoutingProtocol"].lower(
            ):
                cmd = hub_tunnel_config_eigrp
                cmd = cmd.format(
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr),
                    RoutingProtocolASN=str(
                        self.section_dict['dmvpn']["RoutingProtocolASN"]),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    AuthString=self.section_dict['dmvpn']["NHRPAuthString"],
                    NHRPNetworkId=str(
                        self.section_dict['dmvpn']["NHRPNetworkId"]),
                    TunnelKey=str(
                        self.section_dict['dmvpn']["TunnelKey"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"])
            elif 'bgp' in self.section_dict['dmvpn']["RoutingProtocol"].lower():
                cmd = hub_tunnel_config_bgp
                cmd = cmd.format(
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    AuthString=self.section_dict['dmvpn']["NHRPAuthString"],
                    NHRPNetworkId=str(
                        self.section_dict['dmvpn']["NHRPNetworkId"]),
                    TunnelKey=str(
                        self.section_dict['dmvpn']["TunnelKey"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"])
        else:
            try:
                hub1_pip = self.section_dict['hub-1']['pip']
            except KeyError:
                return None
            try:
                hub2_pip = self.section_dict['hub-2']['pip']
            except (KeyError, TypeError) as e:
                log.info('[ERROR] No HUB-2 dict was found! {}'.format(e))
                hub2_pip = None
            if hub2_pip is not None:
                cmd = spoke_tunnel_config_general
                cmd = cmd.format(
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    AuthString=self.section_dict['dmvpn']["NHRPAuthString"],
                    DMVPNHubTunnelIp1=str(
                        self.section_dict['dmvpn']["DMVPNHubTunnelIp1"]),
                    DMVPNHubIp1=str(hub1_pip),
                    DMVPNHubTunnelIp2=str(
                        self.section_dict['dmvpn']["DMVPNHubTunnelIp2"]),
                    DMVPNHubIp2=str(hub2_pip),
                    NHRPNetworkId=str(
                        self.section_dict['dmvpn']["NHRPNetworkId"]),
                    TunnelKey=str(
                        self.section_dict['dmvpn']["TunnelKey"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"])
            else:
                cmd = spoke_tunnel_config_general_singlehub
                cmd = cmd.format(
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    AuthString=self.section_dict['dmvpn']["NHRPAuthString"],
                    DMVPNHubTunnelIp1=str(
                        self.section_dict['dmvpn']["DMVPNHubTunnelIp1"]),
                    DMVPNHubIp1=str(hub1_pip),
                    NHRPNetworkId=str(
                        self.section_dict['dmvpn']["NHRPNetworkId"]),
                    TunnelKey=str(
                        self.section_dict['dmvpn']["TunnelKey"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"])
        output = self.cmd_configure(cmd)
        log.info(output)
        self.cmd_execute(
            "send log [INFO] [CSRTransitVNET] Configured {} tunnel ".format(role))

    def configure_routing(self, tunn_addr):

        role = self.section_dict['role'].lower()

        if 'eigrp' in self.section_dict['dmvpn']["RoutingProtocol"].lower():
            if 'hub' in role:
                cmd = routing_eigrp_vrf
                cmd = cmd.format(
                    RoutingProtocolASN=str(
                        self.section_dict['dmvpn']["RoutingProtocolASN"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"],
                    DMVPNTunnelIpNetworkNum=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpNetworkNum"]),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr))
            else:
                cmd = routing_eigrp
                cmd = cmd.format(
                    RoutingProtocolASN=str(
                        self.section_dict['dmvpn']["RoutingProtocolASN"]),
                    DMVPNTunnelIpNetworkNum=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpNetworkNum"]),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr))
        elif 'bgp' in self.section_dict['dmvpn']["RoutingProtocol"].lower():
            if 'hub' in role:
                cmd = routing_bgp_vrf
                cmd = cmd.format(
                    RoutingProtocolASN=str(
                        self.section_dict['dmvpn']["RoutingProtocolASN"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"],
                    DMVPNTunnelIpNetworkNum=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpNetworkNum"]),
                    DMVPNTunnelIpPrefixLen=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpPrefixLen"]),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr))
            else:
                cmd = routing_bgp
                cmd = cmd.format(
                    RoutingProtocolASN=str(
                        self.section_dict['dmvpn']["RoutingProtocolASN"]), DMVPNTunnelIpNetworkNum=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpNetworkNum"]), DMVPNHubTunnelIp1=str(
                        self.section_dict['dmvpn']["DMVPNHubTunnelIp1"]), DMVPNHubTunnelIp2=str(
                        self.section_dict['dmvpn']["DMVPNHubTunnelIp2"]), TunnelIP=str(tunn_addr))

        output = self.cmd_configure(cmd)
        log.info("cfg routing output = %s" % output)

        self.cmd_execute(
            "send log [INFO] [AzureTransitVNET] Configured {} {} routing.".format(
                role, self.section_dict['dmvpn']["RoutingProtocol"].lower()))

    def configure_crypto_policy(self):
        '''
        This functions is responsible for configuring the router with appropriate Crypto Policy.
        Right now, we will be configuring the general crypto policy (See py variable crypto_policy_general)

        The config string is appended accordingly with fields from self.section_dict

        Args:
            ROLE, SECTION_DICT

        Returns:
            None

        '''
        role = self.section_dict['role'].lower()

        if 'hub' in role:
            vrf_config = hub_vrf_config.format(
                ConnName=self.section_dict['dmvpn']["ConnectionName"],
                TunnelId=self.section_dict['dmvpn']["TunnelID"],
                RoutingProtocolASN=str(
                    self.section_dict['dmvpn']["RoutingProtocolASN"]))
            output = self.cmd_configure(vrf_config)
            log.info("[INFO] [CSRTransitVNET] Configured HUB VRF successfully")
            log.info("output = %s" % output)
            self.cmd_execute(
                "send log [INFO] [CSRTransitVNET] Configured HUB VRF successfully")

        crypto_config = crypto_policy_general.format(
            ConnName=self.section_dict['dmvpn']["ConnectionName"],
            TunnelId=self.section_dict['dmvpn']["TunnelID"],
            SharedKey=self.section_dict['dmvpn']["SharedKey"],
            IpsecCipher=self.section_dict['dmvpn']["IpsecCipher"],
            IpsecAuthentication=self.section_dict['dmvpn']["IpsecAuthentication"])

        output = self.cmd_configure(crypto_config)
        log.info(
            '[INFO] [CSRTransitVNET] Configured crypto policy general successfully')
        log.info("crypto policy output = %s" % output)

        self.cmd_execute(
            "send log [INFO] [CSRTransitVNET] Configured crypto policy general successfully")

    def get_tunnel_addr(self):
        tunn_addr = None
        role = self.section_dict['role'].lower()
        tunnel_network = self.section_dict['DMVPNTunnelIpCidr']
        if 'hub' in role:
            log.info('[INFO] Configuring router as {}'.format(role))
            hub_dict = {}
            hub_dict['pip'] = self.cloud.get_pip()
            self.section_dict['spoke'] = {'count': 0}
            if '1' in role:
                tunn_addr = tunnel_network.network_address + 1
                hub_dict['nbma'] = str(tunn_addr)
                self.section_dict['hub-1'] = hub_dict
            else:
                tunn_addr = tunnel_network.network_address + 2
                hub_dict['nbma'] = str(tunn_addr)
                self.section_dict['hub-2'] = hub_dict
        elif role == 'spoke':
            log.info('[INFO] Configuring router as SPOKE')
            try:
                dmvpn_address_count = tunnel_network.num_addresses
                spoke_vmid = self.cloud.get_vmid()
                spoke_pip = self.cloud.get_pip()
                random.seed(spoke_vmid)
                rand_tunn_offset = random.randint(10, dmvpn_address_count)
                self.section_dict['spoke']['count'] = int(
                    self.section_dict['spoke']['count'])
                self.section_dict['spoke']['count'] += 1
                tunn_addr = tunnel_network.network_address + rand_tunn_offset
                self.section_dict['spoke'][spoke_vmid] = {
                    'pip': str(spoke_pip), 'tunnel_address': str(tunn_addr)}
            except KeyError:
                log.info(
                    '[ERROR] Spoke count is not found in spoke file contents.')
                return None
        else:
            log.info('[ERROR] Unrecognized role is assigned to the router!')

        return tunn_addr

    def configure_transit_vnet(self):
        tunn_addr = self.get_tunnel_addr()
        self.write_all_files()
        self.configure_crypto_policy()
        self.configure_tunnel(tunn_addr)
        self.configure_routing(tunn_addr)
        self.cmd_execute(
            "send log [INFO] [AzureTransitVNET] Success. Configured all the required IOS configs.".format(role))

    def setup_dmvpn_dict(self):
        param_list = ['TunnelKey', 'RoutingProtocol', 'transitvnetname']
        dmvpn_dict = {}
        for param in param_list:
            dmvpn_dict[param] = self.section_dict[param]
        return dmvpn_dict

    # todo: need keyword from cloud file ?
    def parse_decoded_custom_data(self, keyword='AzureTransitVnet'):
        section_flag = False
        try:
            with open(self.cd_file) as filecontents:
                for line in filecontents:
                    if 'section:' in line:
                        if keyword in line:
                            section_flag = True
                        else:
                            section_flag = False

                    if section_flag:
                        split_line = line.split(' ')
                        if len(split_line) == 2:
                            self.section_dict[split_line[0].strip(
                            )] = split_line[1].strip()
                        else:
                            log.info(
                                '[ERROR] command parsing failed for %s' %
                                str(split_line))
        except IOError as e:
            log.exception('[ERROR] %s' % e)
            return False

        log.info(self.section_dict)
        return True

    def write_all_files(self):
        if 'hub-1' in self.section_dict['role']:
            file_list = ['spoke', 'hub-1', 'dmvpn']
        elif 'hub-2' in self.section_dict['role']:
            file_list = ['spoke', 'hub-2', 'dmvpn']
        elif 'spoke' in self.section_dict['role']:
            file_list = ['spoke']

        for file_content in file_list:
            try:
                file_contents = self.section_dict[file_content]
                file_name = self.section_dict['file_names'][file_content]
                log.info(
                    '[INFO] Savings contents for {} in {} with {}'.format(
                        file_content, file_name, str(file_contents)))
                self.cloud.write_file_contents(
                    self.section_dict['file_share'],
                    self.section_dict['folder'],
                    file_name,
                    file_contents)
            except KeyError:
                log.info(
                    '[ERROR] could not save file for {}'.format(file_content))

    def get_all_files(self):
        if 'spoke' in self.section_dict['role']:
            file_list = ['spoke', 'hub-1', 'hub-2', 'dmvpn']
        else:
            file_list = ['dmvpn']

        hub_1_flag = False
        if 'hub' in self.section_dict['role']:
            hub_1_flag = True
        elif 'spoke' in self.section_dict['role']:
            hub_one_file = self.cloud.file_exists(
                self.section_dict['file_share'],
                self.section_dict['folder'],
                self.section_dict['file_names']['hub-1'])
            hub_two_file = self.cloud.file_exists(
                self.section_dict['file_share'],
                self.section_dict['folder'],
                self.section_dict['file_names']['hub-2'])

            if hub_one_file and not hub_two_file:
                file_list = ['spoke', 'hub-1', 'dmvpn']
                self.section_dict['hub-2'] = {
                    'pip': '255.255.255.254', 'nbma': '1.1.1.2'}
            elif not hub_one_file and hub_two_file:
                file_list = ['spoke', 'hub-2', 'dmvpn']
                self.section_dict['hub-1'] = {
                    'pip': '255.255.255.254', 'nbma': '1.1.1.1'}

        for file_content in file_list:
            contents = None
            tries = 0
            while contents is not None:
                log.info(
                    '{} {} {}'.format(
                        self.section_dict['file_share'],
                        self.section_dict['folder'],
                        self.section_dict['file_names'][file_content]))
                contents = self.cloud.get_file_contents_json(
                    self.section_dict['file_share'],
                    self.section_dict['folder'],
                    self.section_dict['file_names'][file_content])
                if contents:
                    log.info(
                        '[INFO] Retrieved file contents for {}: {}'.format(
                            file_content, str(contents)))
                else:
                    if hub_1_flag:
                        break
                    log.info(
                        '[ERROR] Error while retrieving {}. Try num: {}'.format(
                            file_content, str(tries)))
                    time.sleep(50)
                    tries += 1
            if contents:
                self.section_dict[file_content] = contents
        return self.section_dict

    def setup_file_dict(self):
        self.section_dict['folder'] = 'config'
        self.section_dict['file_names'] = {
            'hub-1': 'hub1.json',
            'hub-2': 'hub2.json',
            'spoke': 'spokes.json',
            'dmvpn': 'dmvpn.json'}
        try:
            file_share = self.section_dict['transitvnetname']
            self.section_dict['file_share'] = file_share
        except KeyError:
            file_share = 'new'
            self.section_dict['file_share'] = file_share

    def setup_default_dict(self):

        try:
            DMVPNTunnelIpCidrStr = self.section_dict['dmvpn']['DMVPNTunnelIpCidr']
        except KeyError:
            DMVPNTunnelIpCidrStr = '1.1.1.0/24'

        DMVPNTunnelIpCidr = ipaddress.IPv4Network(
            DMVPNTunnelIpCidrStr.decode('utf-8'))
        self.section_dict['DMVPNTunnelIpCidr'] = DMVPNTunnelIpCidr

        if 'dmvpn' not in self.section_dict:
            self.section_dict['dmvpn'] = {}

        default_dict = {
            "ConnectionName": "tvnet",
            "RoutingProtocol": "EIGRP",
            "TunnelID": 11,
            "TunnelKey": 0o12210,
            "SharedKey": 'ciscokey',
            "IpsecCipher": "esp-aes",
            "IpsecAuthentication": "esp-sha-hmac",
            "RoutingProtocolASN": 64512,
            "NHRPAuthString": 'cisco',
            "NHRPNetworkId": 1024
        }

        for key, value in default_dict.items():
            try:
                self.section_dict[key]
                self.section_dict['dmvpn'][key] = self.section_dict[key]
            except KeyError:
                try:
                    self.section_dict['dmvpn'][key]
                    self.section_dict[key] = self.section_dict['dmvpn'][key]
                except KeyError:
                    self.section_dict[key] = value
                    self.section_dict['dmvpn'][key] = value

        tunnel_addressing_dict = {
            "DMVPNTunnelIpCidr": DMVPNTunnelIpCidr,
            "DMVPNHubTunnelIp1": DMVPNTunnelIpCidr.network_address + 1,
            "DMVPNHubTunnelIp2": DMVPNTunnelIpCidr.network_address + 2,
            "DMVPNTunnelIpMask": DMVPNTunnelIpCidr.netmask,
            "DMVPNTunnelIpNetworkNum": DMVPNTunnelIpCidr.network_address,
            "DMVPNTunnelIpHostMask": DMVPNTunnelIpCidr.hostmask,
            "DMVPNTunnelIpPrefixLen": DMVPNTunnelIpCidr.prefixlen
        }

        for key, value in tunnel_addressing_dict.items():
            self.section_dict[key] = value
            self.section_dict['dmvpn'][key] = value
