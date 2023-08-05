'''

Copyright (c) 2016-2017 Vanessa Sochat

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from rest_framework import status

from shub.apps.main.models import Container

from shub.apps.api.utils import get_instance_name

from shub.settings import (
    QUEUE_ACTIVE,
    DEFAULT_BUILD_FILE,
    GOOGLE_CLOUD_PROJECT, 
    GOOGLE_CLOUD_ZONE, 
    GOOGLE_CLOUD_BUILDER_IMAGE, 
    GOOGLE_CLOUD_BUCKET
)

from singularity.build.utils import get_build_template
from singularity.build.google import (
    get_bucket,
    delete_object
)

import json
import os
import re
import requests
from retrying import retry
import time


#####################################################################################
# SERVICE
#####################################################################################

def get_google_service(service_type=None,version=None):
    '''
    get_url will use the requests library to get a url
    :param service_type: the service to get (default is compute)
    :param version: version to use (default is v1)
    '''
    if service_type == None:
        service_type = "compute"
    if version == None:
        version = "v1"

    credentials = GoogleCredentials.get_application_default()
    service = discovery.build(service_type, version, credentials=credentials) 
    return service


def operation_complete(service, project, zone, operation, container=None, status=None):
    '''wait for operation is a helper function
    https://cloud.google.com/compute/docs/tutorials/python-guide
    to ensure that an operation finished
    :param service: the service from get_google_service
    :param project, zone: specific to the project
    :param operation: the "name" field of the insert (or other) response
    :param build: optional, a build, container.status set to 'status' on fail 
    :param status_change: the status to change the container.status to.
    '''
    if status == None:
        status = "ERROR"

    while True:
        result = service.zoneOperations().get(project=project,
                                              zone=zone,
                                              operation=operation).execute()

        if result['status'] == 'DONE':
            if 'error' in result:
               if container is not None:
                   container.status = status
                   container.save()
               raise Exception(result['error'])
            return result
        time.sleep(1)



#####################################################################################
# GOOGLE STORAGE
#####################################################################################


def delete_storage_files(files):
    '''delete_storage_files will delete files in Google Storage, done after an instance
    is deleted.
    :param files: one or more files to delete.
    '''
    if not isinstance(files,list):
        files = [files]

    service = get_google_service(service_type="storage")
    bucket = get_bucket(service,GOOGLE_CLOUD_BUCKET)
    for file_object in files:
        if isinstance(file_object,dict):
            if "kind" in file_object:
                if file_object['kind'] == "storage#object":
                    object_name = "/".join(file_object['id'].split('/')[:-1])
                    object_name = re.sub('%s/' %bucket['name'],'',object_name,1)
                    delete_object(service,bucket['name'],object_name)
                    

#####################################################################################
# GOOGLE COMPUTE ENGINE
#####################################################################################


def list_instances(project=None, zone=None):
    '''list_instances will take a service, project, and zone, and list images
    https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/compute/api/create_instance.py#L36
    '''
    service = get_google_service()  # default is compute

    # If no instance name provided, use default builder        
    if project == None:
        project = GOOGLE_CLOUD_PROJECT
    if zone == None:
        zone = GOOGLE_CLOUD_ZONE

    instances = service.instances().list(project=project, zone=zone).execute()
    return instances['items']



@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=3)
def destroy_instance(container, container_id):
    '''destroy_instance will take down an instance
    :param container: the build container to cancel (to generate the instance name)
    :param container_id: explicitly put in case container has been deleted and has no id
    '''
    instance_name = get_instance_name(container, container_id)

    instances = list_instances()
    instances = [x for x in instances if x['name'] == instance_name]

    if len(instances) > 0:
        service = get_google_service()
        return service.instances().delete(project=GOOGLE_CLOUD_PROJECT, 
                                   zone=GOOGLE_CLOUD_ZONE, 
                                   instance=instance_name).execute()


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=3)
def insert_instance(service, config):
    '''insert instance will add a retry to creating a new instance, in case it fails.
    '''
    operation = service.instances().insert(project=GOOGLE_CLOUD_PROJECT,
                                           zone=GOOGLE_CLOUD_ZONE,
                                           body=config).execute()
    return operation


def setup_google_build(container,
                       machine_type=None,
                       storage_bucket=None,
                       metadata=None,
                       do_move=True):

    '''setup_google_build will update the metadata to include the complete instance config
    :param build: the Queue object with the build
    :param metadata: any metadata to send to the build.
    '''
    from shub.apps.api.queue import move_queue

    if machine_type == None:
        machine_type = "n1-standard-1"

    # Get saved build specs
    container.save()
    instance_name = get_instance_name(container, container.id)
    builder = container.collection.get_builder('gce')
    image_name = builder.specs['builder_name']
    storage_bucket = builder.specs['bucket_name']

    service = get_google_service()
    image_response = service.images().get(project=GOOGLE_CLOUD_PROJECT, 
                                          image=image_name).execute()

    # Get the source image disk
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/%s" %(GOOGLE_CLOUD_ZONE,machine_type)

    # Default uses singularity (dev) latest
    startup_script = get_build_template(DEFAULT_BUILD_FILE)

    config = {
        'name': instance_name,
        'machineType': machine_type,
        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],
        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],
        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/compute',
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],
        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }
           ]
        }
    }

    # Add the meta data
    if metadata == None:
        metadata = dict()

    # This tells the start script to build, other option is to set entire script at runtime
    metadata['dobuild'] = True
    metadata['bucket_name'] = storage_bucket
    metadata['container_id'] = container.id

    for key,value in metadata.items():
        entry = {"key":key,'value':value}
        config['metadata']['items'].append(entry)

    # Add the updated metadata (the completed build information)
    container.queue.build_spec = json.dumps(config)
    container.queue.queue_type = "PENDING"
    container.queue.save()
    container.status = "PENDING"
    container.save()

    # Add the container to the collection.s queue
    builder.queue.add(container.queue)
    builder.save()
    container.collection.save()

    # The build runs right away if the queue was empty
    if do_move is True:
        move_queue(collection=container.collection,
                   build_env="gce")

    return 200



def run_google_build(container):
    '''run_google_build will build an image after a push event to a repo
    '''
    # Use standard name so we know how to delete later
    container.save() # ensure has an id
    name = get_instance_name(container, container.id)
    build = container.queue

    # One more check of the container status
    if container.status != "RUNNING" and build.queue_type == "PENDING" and QUEUE_ACTIVE:

        # Get the service, and submit the build
        service = get_google_service()

        # Load the config
        config = json.loads(build.build_spec)

        # The container status must be updated to running, or
        # else other builds will be triggered
        container.status = 'WAITING'        
        container.save()

        try:
            operation = insert_instance(service, config)
            response = operation_complete(service=service,
                                          project=GOOGLE_CLOUD_PROJECT,
                                          operation=operation['name'],
                                          zone=GOOGLE_CLOUD_ZONE,
                                          container=container)

            # Move to active queue
            build.queue_type = "ACTIVE"
            build.save()

            build_status = {"message":"Build received.",
                            "status":200,
                            "status_message":"RUNNING"}
   
            container.status = 'RUNNING'
            container.save()


        except:

            container.status = 'PENDING'        
            container.save()

            build_status = {"message":"Build already running",
                            "status": 403,
                            "status_message":"WAITING"}


    else:    

        build_status = {"message":"Build already running",
                        "status":200,
                        "status_message":"RUNNING"}

    return build_status
