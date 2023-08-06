'''
Created on Mar 19, 2018

@author: jliu
'''
import os
import logging
from paramiko import SSHClient
from paramiko import AutoAddPolicy
from scp import SCPClient
from pssh.ssh2_client import SSHClient as PSSHClient

logger = logging.getLogger('fjord_kafka_migration')


class BrokerDataCopier(object):
    '''
    Broker data copier is mainly used to sync data from remote broker server to the local server.
    '''

    def __init__(self, remote_username, remote_password, remote_host, remote_path, local_path):
        '''
        Constructor for broker data copier.
        :param remote_username is the remote login name.
        :param remote_password is the remote login password.
        :param remote_host is the remote server host.
        :param remote_path is the path in the remote server.
        :param local_path is the local path to store copied files.
        '''
        self.remote_username = remote_username
        self.remote_password = remote_password
        self.remote_host = remote_host
        self.remote_path = remote_path
        self.local_path = local_path
        
        pass
    
    def do_pssh_copy(self):
        '''
        leverage parallel ssh to improve file copying speeds.
        '''
        try:
            logger.info("check local path %s exist or not.", self.local_path)
            self.check_dir_exist(self.local_path)
        
            logger.info("create a shared pssh client with server login info host = %s, user = %s, password = ****.", self.remote_host, self.remote_username)
            self.pssh = PSSHClient(self.remote_host, user=self.remote_username, password=self.remote_password)
        
            logger.info("start to copy files from remote %s:%s to 127.0.0.1:%s.", self.remote_host, self.remote_path, self.local_path)
            self.pssh.copy_remote_file(remote_file=self.remote_path, local_file=self.local_path, recurse=True)
        
            logger.info("done to copy remote files.")
        except Exception as e:
            logger.error("error occurred during parallel ssh file coping, the error is %s.", e)
            raise e

        pass
     
    def do_scp_copy(self):
        """
        leverage scp to do file copying.
        """
        try:
            logger.info("check file path %s is exist in local.", self.local_path)
            self.check_dir_exist(self.local_path)
        
            # build ssh channel
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.load_system_host_keys()
            ssh.connect(hostname=self.remote_host, username=self.remote_username, password=self.remote_password)
        
            # leverage ssh channel, run scp command on hosted server
            with SCPClient(ssh.get_transport(), sanitize=lambda x: x, progress=self.show_scp_progress) as scp:
                logger.info("start to copy files with scp.")
                scp.get(remote_path=self.remote_path, local_path=self.local_path, recursive=True, preserve_times=True)
       
                logger.info("done to copy files from %s:%s to local %s.", self.remote_host, self.remote_path, self.local_path) 
        except Exception as e:
            logger.error("error occurred during scp file copying, the error is %s.", e)
            raise e
        
        pass
    
    def show_scp_progress(self, filename, size, sent):
        logger.debug("%s %s %s", filename, str(size), str(sent))
        pass
    
    def check_dir_exist(self, dir_path):
        if not os.path.exists(dir_path):
            logger.error("the folder with %s is not exist", dir_path)
            raise Exception("the folder with %s does not exist.", dir_path)
        else:
            logger.info("the folder with %s exists.", dir_path)
            pass
