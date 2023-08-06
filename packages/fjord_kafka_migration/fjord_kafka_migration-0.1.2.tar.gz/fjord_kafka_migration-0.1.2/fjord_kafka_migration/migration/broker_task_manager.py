'''
Created on Mar 20, 2018

@author: jliu
'''
from boto3.session import Session
from botocore.exceptions import ClientError
import time
from boto3.resources import response
import logging

logger = logging.getLogger('fjord_kafka_migration')


class BrokerTaskManager(object):
    '''
    Broker task manager will be used to manage broker task.
    '''

    def __init__(self, region=None, profile=None, cluster_name=None, task_definition=None, remote_container_id=None, local_container_id=None):
        '''
        Constructor for broker task manager.
        :param region is aws region, e.g us-west-2, eu-central-1
        :param profile is used to authenticate when you develop code on the local.
        :param cluster_name is the cluster name.
        :param task_definition is the task definition name in cluster.
        :param remote_container_id is the remote container id.
        :param local_container_id is the current container id.
        '''
        self.cluster_name = cluster_name
        self.task_definition = task_definition
        self.remote_container_id = remote_container_id
        self.local_container_id = local_container_id
        splits = self.task_definition.split(":")
        if len(splits) != 2:
            raise Exception("the task definition with {} is invalid format, please check and fix it.", self.task_definition)
        else:
            self.familyPrefix = splits[0]
        
        # build client for ecs and ec2
        logger.debug("create instance for ec2 and ecs.")
        session = Session(region_name=region, profile_name=profile)
        self.ecs = session.client(u'ecs')
        self.ec2 = session.client(u'ec2')
        
        # validate resource existing status
        self.__validate()
    
    def __validate(self): 
        try:
            logger.info("validate pass through parameters.")
            
            # check local container id 
            logger.info("validate whether there is a running task in container {} in cluster {}.", self.local_container_id, self.cluster_name)
            response = self.ecs.list_tasks(cluster=self.cluster_name, containerInstance=self.local_container_id, maxResults=2)
            if len(response[u'taskArns']) > 0:
                raise Exception("validation error: there is a running task in the local container with {}, please check and fix it.", self.local_container_id)
            else:
                logger.info("validation success: local container with {} doesn't have task running in cluster {}.", self.local_container_id, self.cluster_name)
            
            # check remote container id  
            logger.info("validate whether there is a running task in container {} in cluster {}.", self.remote_container_id, self.cluster_name)  
            response = self.ecs.list_tasks(cluster=self.cluster_name, containerInstance=self.remote_container_id, maxResults=2)
            if len(response[u'taskArns']) != 1:
                raise Exception("validation error: there is no running task in the remote container with {}, please check and fix it.", self.remote_container_id)
            else:
                logger.info("validation success: remote container with {} does have a task running in cluster {}.", self.remote_container_id, self.cluster_name)
            
            # check task definition    
            logger.info("validate whether there is a task definition with {} exist or not.", self.task_definition)
            response = self.ecs.list_task_definitions(familyPrefix=self.familyPrefix, maxResults=2)
            if len(response[u'taskDefinitionArns']) > 0:
                found = False
                for taskDefinitionArn in response[u'taskDefinitionArns']:
                    if taskDefinitionArn.index(self.task_definition) > -1:
                        found = True
                        break
                
                if not found:
                    raise Exception("validation error: there is no task definition with {} , please check and fix it.", self.task_definition)
                else:
                    logger.info("validation success: task definition with {} is valid.", self.task_definition)
                    
            else:
                raise Exception("validation error: there is no task definition with {} , please check and fix it.", self.task_definition)
            
            logger.info("validate pass through parameters done.")
            
        except Exception as error:
            raise error;
        
        pass
     
    def stop_broker_task(self, container_id):
        '''
        stop the task with the container id. 
        '''
        try:
            logger.info("Initiating stop task.")
            task_arn = self.get_broker_task(container_id)
            response = self.ecs.stop_task(cluster=self.cluster_name, task=task_arn, reason='fjord migration does need to stop the task.')
            logger.debug("the response for stopping task is %s.", response)
            logger.info("it's success to stop the task %s with container id %s.", task_arn, container_id)
            
            # check stopped task status
            while self.get_broker_task(container_id, u'STOPPED') is None:
                logger.info("wait for 1 second to check task %s stopping status again.", task_arn)
                time.sleep(1)
            
            logger.info("the task %s running in container %s has been stopped successfully." , task_arn, container_id)
            
        except ClientError as e:
            logger.error("error happened during stop task %s, the error returned is %s.", task_arn, e)
            raise e
        
        pass
    
    def start_broker_task(self, container_id):
        '''
        start a new task in the specific container.
        '''
        try:
            # start a new task in the local container
            response = self.ecs.start_task(cluster=self.cluster_name,
                                           taskDefinition=self.task_definition,
                                           containerInstances=[container_id])
            
            logger.debug("the response returned starting task : %s.", response)
            
            logger.info("start to check task running status ... ")

            # pending check to make sure task is running
            while self.get_broker_task(container_id) is None:
                logger.info("sleep 1 second to check task running status again.")
                time.sleep(1)
            
            logger.info("it's success to detect task running in container %s now.", container_id)
            
        except ClientError as e:
            logger.error("error happened during starting a new task in container %s. the error is %s.", container_id, e)
            raise e
        
        pass
    
    def drain_broker_ec2(self, container_id):
        '''
        drain out a ec2. 
        '''
        try:
            logger.info("start to drain a container %s out of cluster %s.", container_id, self.cluster_name)
            response = self.ecs.update_container_instances_state(
                cluster=self.cluster_name,
                containerInstances=[container_id],
                status='DRAINING')
            
            logger.debug("the response returned after draining container is %s.", response)
            logger.info("it's success to drain container %s out of cluster %s.", container_id, response)
            
        except ClientError as e:
            logger.error("error occurred during draining container, the error is %s.", e)
            raise e
        
        pass
        
    def get_broker_ec2id(self, container_id):
        '''
        get ec2 instance id with specific container.
        '''
        try:
            logger.info("start to describe container %s.", container_id)
            response = self.ecs.describe_container_instances(
                cluster=self.cluster_name,
                containerInstances=[container_id])
            containerInstances = response[u'containerInstances']
            logger.debug("response returned get broker ec2 is %s.", response)
            
            logger.info("it's success to get broker ec2 id with container %s.", container_id)
            if len(containerInstances) > 0:
                containerInstance = containerInstances[0]
                logger.debug("the detail of the container %s is %s." , container_id, containerInstance)
                return containerInstance[u'ec2InstanceId']
            else:
                logger.info("there is no ec2 found with container %s.", container_id)
                return None
            
        except ClientError as e:
            logger.error("error happened during get broker ec2 id with container %s, the error is %s.", container_id, e) 
            raise e
            
        pass
    
    def get_broker_task(self, container_id, status=u'RUNNING'):
        try:
            '''
            get broker task running in container.
            '''
            logger.info("start to list tasks existed in container %s from cluster %s.", container_id, self.cluster_name)
            response = self.ecs.list_tasks(cluster=self.cluster_name, containerInstance=container_id, maxResults=2, desiredStatus=status)
            task_arns = response[u'taskArns']
            logger.debug("the response returned get broker task is %s.", response)
            
            logger.info("it's success to get the task arns %s from container %s." , container_id, task_arns)
            if len(task_arns) > 0:
                return task_arns[0] 
            else:
                logger.info("there is no task found in container %s.", container_id)
                return None
            
        except ClientError as e:
            logger.error("error happened during get broker task in container %s, the error is %s." , container_id, e)
            raise e
        
        pass
    
    def get_broker_ipaddress(self, instance_id):   
        '''
        get broker ip address with ec2 instance id.
        ''' 
        try:
            logger.info("start to get ec2 ip address with %s.", instance_id)
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            logger.debug("response returned after describing ec2 instance is %s.", response)

            if len(response[u'Reservations']) > 0:
                reservation = response[u'Reservations'][0]
                if len(reservation[u'Instances']) > 0:
                    instance = reservation[u'Instances'][0]
                    logger.debug("the detail for instance %s is %s.", instance_id, instance)
                    ip_address = instance[u'PrivateIpAddress']
                    
                logger.info("the ip address is %s for instance %s." , ip_address, instance_id)
                
                return ip_address
            else:
                logger.info("there is no ip address found with container id %s.", instance_id)
                return None
            
        except ClientError as e:
            logger.error("error occurred during get ip address for instance %s, the error is %s." , instance_id, e)
            raise e
        
        pass
