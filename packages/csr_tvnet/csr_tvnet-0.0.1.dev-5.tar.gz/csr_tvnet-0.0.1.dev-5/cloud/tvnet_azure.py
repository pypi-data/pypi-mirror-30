#!/usr/bin/env python

'''
Cisco Copyright 2018
Author: Vamsi Kalapala <vakalapa@cisco.com>

FILENAME: AZURESTORAGE.PY


'''
from azure.storage.file import FileService
import json
import logging
import urllib2

log = logging.getLogger('csr_tvnet')

metadata_url = 'http://169.254.169.254/metadata/instance?api-version=2017-03-01'
headers = {'Metadata': 'true'}
'''
https://azure-storage.readthedocs.io/en/latest/ref/azure.storage.file.fileservice.html

'''


class azure_tvnet():
    def __init__(self, account_name, account_key):
        self.metadata = self.get_metadata()
        self.azure_file_service = FileService(
            account_name=account_name, account_key=account_key)

    def get_file_contents(self, file_share, folder, file_name):
        is_file = self.azure_file_service.exists(
            file_share, directory_name=folder, file_name=file_name)
        if is_file:
            filedata = self.azure_file_service.get_file_to_text(
                file_share, folder, file_name)
            log.info(filedata.content)
            # filedata_json =  json.loads(filedata.content)
            return filedata.content
        else:
            return None

    def file_exists(self, file_share, folder, file_name):
        return self.azure_file_service.exists(
            file_share, directory_name=folder, file_name=file_name)

    def write_file_contents(
            self,
            file_share,
            folder,
            file_name,
            file_contents):
        self.azure_file_service.create_share(file_share)
        self.azure_file_service.create_directory(file_share, folder)
        for k, v in file_contents.items():
            file_contents[k] = str(v)
        output = self.azure_file_service.create_file_from_text(
            file_share, folder, file_name, json.dumps(file_contents))
        return output

    def get_file_contents_json(self, file_share, folder, file_name):
        output = self.get_file_contents(file_share, folder, file_name)
        if output is not None:
            return json.loads(output)
        else:
            return None

    def get_metadata(self):
        req = urllib2.Request(metadata_url, headers=headers)
        resp = urllib2.urlopen(req)
        resp_read = resp.read()
        data = json.loads(resp_read)
        return data

    def get_pip(self):
        for i, interface in enumerate(self.metadata["network"]["interface"]):
            for j, ip in enumerate(interface["ipv4"]["ipaddress"]):
                if ip['publicip'] is not u'':
                    log.info("[INFO] Public ip is %s" % ip["publicip"])
                    return ip['publicip']

    def get_vmid(self):
        return self.metadata['compute']['vmId']
