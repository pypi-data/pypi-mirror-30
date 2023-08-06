'''
Created on Mar 19, 2018

@author: jliu
'''
import subprocess
import os
import re
from paramiko import SSHClient
from paramiko import AutoAddPolicy
from scp import SCPClient


class BrokerDataCopier(object):
    '''
    :module BrokerDataCopier is major code used to copy data from the source broker to the specified destination.
    '''

    def __init__(self, remote_username, remote_password, remote_host, remote_path, local_path):
        '''
        Constructor for broker data copier.
        :param remote_username is the remote SSH user.
        :param remote_password is the ssh user password.
        :param remote_host is the remote host, e.g ip address.
        :param remote_path is the path in the remote server.
        :param local_path is the local full path user to remote copied files.
        '''
        self.remote_username = remote_username
        self.remote_password = remote_password
        self.remote_host = remote_host
        self.remote_path = remote_path
        self.local_path = local_path
        
        pass
    
    def do_rsync_copy(self):
        """
        run rync copy need to check the rsynced installed or not firstly.
        """
        
        self.check_dir_exist(self.local_path)
        
        # escapte the 
        escaped_remote_path = re.escape(self.local_path)
        escaped_local_path = re.escape(self.local_path)
        
        # create the rsync command
        rsync_command = "/usr/bin/rsync -va %s@%s:'%s' %s" % (self.remote_username, self.remote_host, escaped_remote_path, escaped_local_path) 
        print('the executed command for rsync will be %s. ' % rsync_command)
        
        # execute rsync copy
        try:
            returned_code = subprocess.Popen(rsync_command, shell=True).wait()
            print("success to execute rsync with command %s and returned code %s" % (rsync_command, returned_code))
        except Exception as error:
            raise Exception('error detected during running command %s is %s' % (rsync_command, error))
        
        pass    
    
    def do_scp_copy(self):
        """
        scp is a pre-installed tool.
        """
        self.check_dir_exist(self.local_path)
        
        # build ssh channel
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=self.remote_host, username=self.remote_username, password=self.remote_password)
        
        # leverage ssh channel, run scp command on hosted server
        with SCPClient(ssh.get_transport(), sanitize=lambda x: x, progress=self.show_scp_progress) as scp:
            scp.get(remote_path=self.remote_path, local_path=self.local_path, recursive=True, preserve_times=True)
       
        print("data copy from %s to local is done." % (self.remote_host)) 

        pass
    
    def show_scp_progress(self, filename, size, sent):
        print("%s %s %s" % (filename, str(size), str(sent)))
        pass
    
    def check_dir_exist(self, dir_path):
        if not os.path.exists(dir_path):
            print('%s does not exist.' % (dir_path))
            exit(1)
        else:
            print('%s does exist.' % (dir_path))
            pass
