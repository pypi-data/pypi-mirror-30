'''
Created on Mar 16, 2018

@author: jliu
'''

import argparse
from migration.broker_data_copier import BrokerDataCopier
from migration.broker_task_manager import BrokerTaskManager


def run():
    """
    This script is used to migrate broker to new one.
    
    scenarios
    =========
    1, ec2 is not promised 100% healthy, so it will be possibly reported retired by aws.
    2, broker ec2 instance may be deployed none security standard, it will be asked to redeploy.
    3, broker server may be unexpected bad performance, it need to migrate to new one.
    4, others.
    
    what does this script do?
    =========
    1, backup data to specific ec2 server.
    2, stop replaced broker.
    3, start new broker.
    """
    
    # parsing the required args.
    parser = argparse.ArgumentParser(description='fjord kafka migration : it is a tool used to move broker to new one and expire the old one .')
    parser.add_argument('--region', default=None, help='the aws region, e.g us-west-2, eu-central-1.')
    parser.add_argument('--profile', default=None, help='the aws profile configured in relative machine.')
    parser.add_argument('--cluster-name', default=None, help='the broker cluster name.')
    parser.add_argument('--task-definition', default=None, help='the running task definition in ecs.')
    parser.add_argument('--remote-container-id', default=None, help='the remote broker container id.')
    parser.add_argument('--local-container-id', default=None, help='the local broker container id.')
    parser.add_argument('--remote-username', default=None, help='the remote server ssh user name.')
    parser.add_argument('--remote-password', default=None, help='the remote server ssh password.')
    parser.add_argument('--local-path', default=u'/ecs/data', help='the local full path which will be used to store copied data.')
    parser.add_argument('--remote-path', default=u'/ecs/data/kafka', help='the remote data full path')
    
    args = parser.parse_args()
    
    print('arguments : %s' % args)
    
    # construct broker task manager 
    remote_container_id = args.remote_container_id
    local_container_id = args.local_container_id
    
    manager = BrokerTaskManager(region=args.region,
                                profile=args.profile,
                                cluster_name=args.cluster_name,
                                task_definition=args.task_definition)
    
    # get remote broker address
    remote_instance_id = manager.get_broker_ec2id(remote_container_id)
    if remote_instance_id is None:
        print('failed to check why can not get ec2 instance id.')
        return 
    
    remote_broker_address = manager.get_broker_ipaddress(remote_instance_id)
    if remote_broker_address is None:
        print('failed to get remote ec2 address, please check before continue.')
        return 
    
    # data copy
    copier = BrokerDataCopier(remote_host=remote_broker_address,
                              remote_username=args.remote_username,
                              remote_password=args.remote_password,
                              remote_path=args.remote_path,
                              local_path=args.local_path)
    copier.do_scp_copy()
    
    # retire remote broker and start replaced task on local broker
    manager.stop_broker_task(remote_container_id)
    print('success to stop broker running in container %s.' % remote_container_id)
     
    # start task in new container
    manager.start_broker_task(local_container_id)
    print('success to start broker running in container %s.' % local_container_id)
    
    print("Configuration!!!, broker migration is done, please sincerely check the Kafka cluster is really working well." % args.cluster_name)

    
if __name__ == '__main__':
    run() 
