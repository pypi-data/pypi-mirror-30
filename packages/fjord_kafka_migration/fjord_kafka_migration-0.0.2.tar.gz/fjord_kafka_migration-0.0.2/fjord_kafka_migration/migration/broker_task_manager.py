'''
Created on Mar 20, 2018

@author: jliu
'''
from boto3.session import Session
from botocore.exceptions import ClientError
import time
from boto3.resources import response


class BrokerTaskManager(object):
    '''
    Broker task manager will be used to manage broker task.
    '''
    def __init__(self, region=None, profile=None, cluster_name=None, task_definition=None):
        '''
        Constructor for broker task manager.
        :param region is the resource aws region, e.g us-west-2, eu-central-1.
        :param profile is used to authentication when we don't have role authentication configured.
        :param cluster_name is the broker cluster name.
        :param task_definition is the running task definition for cluster.
        '''
        self.cluster_name = cluster_name
        self.task_definition = task_definition
        
        # build client for ecs and ec2
        session = Session(region_name=region, profile_name=profile)
        self.ecs = session.client(u'ecs')
        self.ec2 = session.client(u'ec2')
        
    def stop_broker_task(self, container_id):
        '''
        stop the task running inside the specific container. 
        '''
        try:
            task_arn = self.get_broker_task(container_id)
            response = self.ecs.stop_task(cluster=self.cluster_name, task=task_arn, reason='fjord migration needs to stop the running task.')
            print('the response returned after stopping task %s running inside container %s is %s.' % (task_arn, container_id, response))
            
            # check stopped task status
            while self.get_broker_task(container_id, u'STOPPED') is None:
                print('sleep 1 seconds to check stopped status again.')
                time.sleep(1)
            
            print('task % running inside %s has been successfully stopped.' % (task_arn, container_id))
            
        except ClientError as e:
            print('error happened during stop task %s, the error returned is %s.' % (task_arn, e))
            raise e
        
        pass
    
    def start_broker_task(self, container_id):
        '''
        start a new task in the specific container.
        '''
        try:
            # start a new task in the specific container
            response = self.ecs.start_task(cluster=self.cluster_name,
                                           taskDefinition=self.task_definition,
                                           containerInstances=[container_id])
            
            print('the response returned after start broker task is %s.' % response)
            
            # pending check to make sure task is running
            while self.get_broker_task(container_id) is None:
                print('sleep 1 second to check task status again.')
                time.sleep(1)
            
            print('success to detect task is running now inside container %s with returned response %s.' % (container_id, response))
            
        except ClientError as e:
            print('error happened during start a new task in container %s with error %s.' % (container_id, e))
            raise e
        
        pass
    
    def get_broker_ec2id(self, container_id):
        '''
        get ec2 instance id with specific container.
        '''
        try:
            response = self.ecs.describe_container_instances(
                cluster=self.cluster_name,
                containerInstances=[container_id])
            containerInstances = response[u'containerInstances']
            
            print('response returned after calling describe container %s is %s.' % (container_id, response))
            if len(containerInstances) > 0:
                containerInstance = containerInstances[0]
                print('the detail of the container instance is %s.' % containerInstance)
                return containerInstance[u'ec2InstanceId']
            else:
                return None
            
        except ClientError as e:
            print('error happened during get broker ec2 id in container %s, the error is %s.' % (container_id, e)) 
            raise e
            
        pass
    
    def get_broker_task(self, container_id, status=u'RUNNING'):
        try:
            '''
            get broker task running in container.
            '''
            response = self.ecs.list_tasks(cluster=self.cluster_name, containerInstance=container_id, maxResults=2, desiredStatus=status)
            task_arns = response[u'taskArns']
            
            print('the task arns of instance with id %s is %s.' % (container_id, task_arns))
            if len(task_arns) > 0:
                return task_arns[0] 
            else:
                return None
            
        except ClientError as e:
            print("error happened during get broker task for % is %s." % (container_id, e))
            raise e
        
        pass
    
    def get_broker_ipaddress(self, instance_id):   
        '''
        get broker ip address with ec2 instance id.
        ''' 
        try:
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            if len(response[u'Reservations']) > 0:
                reservation = response[u'Reservations'][0]
                if len(reservation[u'Instances']) > 0:
                    instance = reservation[u'Instances'][0]
                    print('the detail of instance %s is %s.' % (instance_id, instance))
                    ip_address = instance[u'PrivateIpAddress']
                    
                print('the ip address for instance with id %s is %s.' % (instance_id, ip_address))
                
                return ip_address
            else:
                return None
            
        except ClientError as e:
            print('ec2 describe error for %s with error %s' % (self.remote_instance_id, e))
            raise e
        
        pass
