'''
Created on Mar 20, 2018

@author: jliu
'''
from boto3.session import Session
from botocore.exceptions import ClientError
import time
from boto3.resources import response
import logging
import shutil, os

logger = logging.getLogger('fjord_kafka_migration')


class BrokerTaskManager(object):
    '''
    Broker task manager will be used to manage broker task.
    '''

    def __init__(self, region=None, profile=None, cluster_name=None, task_definition=None, remote_container_id=None, local_container_id=None, local_path=None):
        '''
        Constructor for broker task manager.
        :param region is aws region, e.g us-west-2, eu-central-1
        :param profile is used to authenticate when you develop code on the local.
        :param cluster_name is the cluster name.
        :param task_definition is the task definition name in cluster.
        :param remote_container_id is the remote container id.
        :param local_container_id is the current container id.
        :param local_path is the local data path.
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
        
        self.local_data_path = local_path
        
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
            logger.info("validate whether there is a running task in container %s in cluster %s.", self.local_container_id, self.cluster_name)
            response = self.ecs.list_tasks(cluster=self.cluster_name, containerInstance=self.local_container_id, maxResults=2)
            if len(response[u'taskArns']) > 0:
                raise Exception("validation error: there is a running task in the local container with %s, please check and fix it.", self.local_container_id)
            else:
                logger.info("validation success: local container with %s doesn't have task running in cluster %s.", self.local_container_id, self.cluster_name)
            
            # check remote container id  
            logger.info("validate whether there is a running task in container %s in cluster %s.", self.remote_container_id, self.cluster_name)  
            response = self.ecs.list_tasks(cluster=self.cluster_name, containerInstance=self.remote_container_id, maxResults=2)
            if len(response[u'taskArns']) != 1:
                raise Exception("validation error: there is no running task in the remote container with %s, please check and fix it.", self.remote_container_id)
            else:
                logger.info("validation success: remote container with %s does have a task running in cluster %s.", self.remote_container_id, self.cluster_name)
            
            # check task definition    
            logger.info("validate whether there is a task definition with %s exist or not.", self.task_definition)
            response = self.ecs.list_task_definitions(familyPrefix=self.familyPrefix, sort='DESC', maxResults=100)
            
            logger.debug("success to list task definitions with family prefix %s, the response is %s.", self.familyPrefix, response)
            if len(response[u'taskDefinitionArns']) > 0:
                found = False
                for taskDefinitionArn in response[u'taskDefinitionArns']:
                    logger.info("loop to look for whether the current task definition %s is including the task %s.", taskDefinitionArn, self.task_definition)
                    if taskDefinitionArn.index(self.task_definition) > -1:
                        found = True
                        break
                
                if not found:
                    raise Exception("validation error: there is no task definition with %s, please check and fix it.", self.task_definition)
                else:
                    logger.info("validation success: task definition with %s is valid.", self.task_definition)
                    
            else:
                raise Exception("validation error: there is no task definition with %s , please check and fix it.", self.task_definition)
            
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
    
    def rollback_broker_task(self, container_id):
        '''
        roll back broker task.
        '''
        try:
            # schedule a new task in the local container
            response = self.update_broker_ec2_state(container_id, u'ACTIVE')
            
            logger.debug("the response returned roll back a task : %s.", response)
            
            logger.info("start to check roll back running status ... ")

            # pending check to make sure task is running
            while self.get_broker_task(container_id) is None:
                logger.info("sleep 1 second to check roll back task running status again.")
                time.sleep(1)
            
            logger.info("it's success to detect roll back task running in container %s now.", container_id)
            
        except ClientError as e:
            logger.error("error happened during roll back a new task in container %s. the error is %s.", container_id, e)
            raise e
        
        pass
    
    def schedule_broker_task(self, container_id):
        '''
        schedule a new task in the specific container.
        '''
        try:
            # schedule a new task in the local container
            response = self.update_broker_ec2_state(container_id, u'ACTIVE')
            
            logger.debug("the response returned schedule a task : %s.", response)
            
            logger.info("start to check task running status ... ")

            # pending check to make sure task is running
            while self.get_broker_task(container_id) is None:
                logger.info("sleep 1 second to check task running status again.")
                time.sleep(1)
            
            logger.info("it's success to detect task running in container %s now.", container_id)
            
        except ClientError as e:
            logger.error("error happened during scheduling a new task in container %s. the error is %s.", container_id, e)
            
            #roll back to draining state
            self.update_broker_ec2_state(container_id, u'DRAINING')
            #clean copied files
            self.__cleanup_folder_contents()
            
            raise e
        
        pass
    
    def update_broker_ec2_state(self, container_id, state):
        '''
        update broker ec2's state.
        '''
        try:
            logger.info("start to update the container %s state to %s in cluster %s.", container_id, state, self.cluster_name)
            response = self.ecs.update_container_instances_state(
                cluster=self.cluster_name,
                containerInstances=[container_id],
                status=state)
            
            logger.debug("the response returned after updating container's state is %s.", response)
            logger.info("it's success to update container %s to state %s in cluster %s.", container_id, state, self.cluster_name)
            
        except ClientError as e:
            logger.error("error occurred during updating container's state, the error is %s.", e)
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
            
            logger.info("it's success to get the task arns %s from container %s." , task_arns, container_id)
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
    
    def __cleanup_folder_contents(self):
        '''
        assist tool used to clean up local copied dirty file or folders, which is part of the work for rolling back local EC2.
        '''
        logger.info("cleanup local copied file or folders under %s.", self.local_data_path)
        for child_file in os.listdir(self.local_data_path):
            child_path = os.path.join(self.local_data_path, child_file)
            try:
                if os.path.isfile(child_path):
                    logger.info("remove local file %s under %s.", child_file, self.local_data_path)
                    os.unlink(child_path)
                else:
                    logger.info("remove local folder %s under %s.", child_file, self.local_data_path)
                    shutil.rmtree(child_path, ignore_errors=True)
            except Exception as e:
                logger.error("error during cleanup local files, the error is %s.", e)
                raise e
            
        pass
        