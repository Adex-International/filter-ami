from datetime import datetime
from datetime import datetime, timedelta
import time
import boto3
from dateutil import parser
import os

TAG_FILTER=os.environ['TAG_FILTER']
EXCLUSION_TAG =os.environ['EXCLUSION_TAG']

def lambda_handler(event, context):

    client = boto3.client('ec2')
    response = client.describe_images(Filters=[{'Name': 'tag:'+TAG_FILTER, 'Values': ['*']}])
    #Keep lastly created three AMIs and remove others
    a=3
    for img in response['Images']:
        datobj = parser.parse(img['CreationDate'])
        datobj.sort()
        if datobj==datobj[a]:
            print(datobj[a])
            a+=1
            delete = True
            for tag in img['Tags']:
                if tag['Key'] == EXCLUSION_TAG and tag['Value'] == 'True':
                    delete = False
            if delete:
                print("Deleting "+img['ImageId']+" "+img['Name'])
                responsederegister = client.deregister_image(ImageId=img['ImageId'])
    #delete unused AMIs
    instances = client.describe_instances()
    used_amis= []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            used_amis.append(instance['ImageId'])
    print(used_amis)
    # Remove duplicate amis
    def remove_duplicates(amis):
        unique_amis = []
        for ami in amis:
            if ami not in unique_amis:
                unique_amis.append(ami)
        return unique_amis
    unique_amis = remove_duplicates(used_amis)
    print(unique_amis)
    #get custom ami from the account
    custom_images = client.describe_images(
        Filters=[
        {
            'Name': 'state',
            'Values': ['available']
        },
    ],
    Owners=['self'],
    ) 
    custom_ami_list=[]
    for image in custom_images['Images']:
        custom_ami_list.append(image['ImageId'])

    for custom_ami in custom_ami_list:
        if custom_ami not in used_amis:
            
            print("deregistering ami {}".format(custom_ami))
            #delete unused AMIs
            client.deregister_image(ImageId=custom_ami)
    return True
