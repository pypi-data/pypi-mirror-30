#!/usr/bin/env python


class cloudapi():
    def __init__(self, account_name, account_key):
        try:
            from azure.storage.file import FileService
            from tvnet_azure import azure_tvnet as cloud
            self.c = cloud(account_name, account_key)
        except IOError as e:
            raise IOError(
                "Azure package not installed! check for other clouds here!")

    def get_file_contents(self, file_share, folder, file_name):
        return self.c.get_file_contents(file_share, folder, file_name)
    
    def list_directory_contents(self, file_share, folder):
        return self.c.get_list_directories_and_files(file_share, folder)

    def file_exists(self, file_share, folder, file_name):
        return self.c.azure_file_service.exists(
            file_share, directory_name=folder, file_name=file_name)

    def write_file_contents(
            self,
            file_share,
            folder,
            file_name,
            file_contents):
        return self.c.write_file_contents(
            file_share, folder, file_name, file_contents)

    def get_file_contents_json(self, file_share, folder, file_name):
        return self.c.get_file_contents_json(file_share, folder, file_name)

    def get_metadata(self):
        return self.c.get_metadata()

    def get_pip(self):
        return self.c.get_pip()
    
    def get_vmid(self):
        return self.c.get_vmid()
    
    def cloud_put_private_key(file_share, folder, local_file_path):
        vmid = self.c.get_vmid()
        file_name = str(vmid) + '.pem'
        privkey_folder = folder +'/privatekeys'
        self.c.create_directory(file_share, privkey_folder)
        self.c.copy_local_file_to_remote(file_share, privkey_folder, file_name, local_file_path)
