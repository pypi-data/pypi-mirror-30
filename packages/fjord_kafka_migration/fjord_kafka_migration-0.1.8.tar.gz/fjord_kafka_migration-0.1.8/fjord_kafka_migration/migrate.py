'''
Created on Mar 16, 2018

@author: jliu
'''

import sys
import argparse
import logging
from migration.broker_data_copier import BrokerDataCopier
from migration.broker_task_manager import BrokerTaskManager


def setup_custom_logger(name, debug=False):
    """
    global cutomized logger configuration.
    """
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # configure log level based on debug required 
    logger = logging.getLogger(name)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    # configure console output    
    logger.addHandler(handler)
    
    return logger

    
def run():
    """
    This script is used to migrate broker to new one.
    
    scenarios
    =========
    1, ec2 is not promised 100% healthy, so it will ask to be retired by aws.
    2, broker server may be asked to redeploy with latest AMI.
    3, broker server may be running with poor performance, and replace the poor broker somehow is needed.
    4, others.
    
    what does this script do?
    =========
    1, backup data for the being replaced broker.
    2, shutdown replaced broker.
    3, launch a new broker.
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
    parser.add_argument('--remote-path', default=u'/ecs/data', help='the remote data full path')
    parser.add_argument('--debug', default=False, help='the remote data full path')
    
    args = parser.parse_args()
    
    logger = setup_custom_logger(name='fjord_kafka_migration', debug=args.debug)
    
    # log console args
    logger.info("the fjord migration passed through arguments : %s.", args)
    
    # construct broker task manager 
    try:
        manager = BrokerTaskManager(region=args.region,
                                profile=args.profile,
                                cluster_name=args.cluster_name,
                                task_definition=args.task_definition,
                                remote_container_id = args.remote_container_id,
                                local_container_id = args.local_container_id)
    except Exception as error:
        logger.error("it's failed to create task manager with error %s, please address the issue and run again.", error)
        sys.exit(1)
        
    # get remote broker address & server instance id
    remote_instance_id = manager.get_broker_ec2id(args.remote_container_id)
    if remote_instance_id is None:
        logger.error("it's failed to retrieve ec2 instance id with container id %s, please address the issue and run again.", args.remote_container_id)
        sys.exit(1)
    
    remote_broker_address = manager.get_broker_ipaddress(remote_instance_id)
    if remote_broker_address is None:
        logger.error("it's failed to get server address with container id %s, the migration will stop processing and wait for your fix.", args.remote_container_id)
        sys.exit(1)
    
    # data copy
    copier = BrokerDataCopier(remote_host=remote_broker_address,
                              remote_username=args.remote_username,
                              remote_password=args.remote_password,
                              remote_path=args.remote_path,
                              local_path=args.local_path)
    try:
        copier.do_pssh_copy()
        logger.info("it's success to migrate data located at %s from remote server %s to local at %s.", args.remote_path, remote_broker_address, args.local_path)
    except Exception as e:
        logger.error('error happened during scp process, the error is %s.', e)
        sys.exit(1)
        
    # drain remote broker ec2, so that we can ensure no task will be replaced any more. 
    try:
        manager.drain_broker_ec2(args.remote_container_id)
        print("it's success to drain container %s out of cluster %s.", args.remote_container_id, args.cluster_name)
    except Exception as e:
        logger.error("error happened during drain broker ec2, the error is %s.", e)
        sys.exit(1)
        
    # retire remote broker and start replaced task on local broker
    try:
        manager.stop_broker_task(args.remote_container_id)
        print(" it's success to stop broker running in container %s.", args.remote_container_id)
    except Exception as e:
        logger.error("error happened during stop broker task, the error is %s.", e)
        sys.exit(1)
        
    # start task in new container
    try:
        manager.start_broker_task(args.local_container_id)
        print("it's success to start a new task running in container %s.", args.local_container_id)
    except Exception as e:
        logger.error("error happened during start a new task, the error is %s.", e)
        sys.exit(1)
        
    print("Congratulations, broker migration is done, please sincerely check the Kafka cluster's status.")

    
if __name__ == '__main__':
    run() 
