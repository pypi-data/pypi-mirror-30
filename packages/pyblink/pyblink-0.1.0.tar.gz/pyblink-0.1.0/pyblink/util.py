import time
from googleapiclient import discovery
from googleapiclient.errors import HttpError


def build_compute():
    return discovery.build('compute', 'v1')


def is_existing_family(family, project, compute=None):

    if compute is None:
        compute = build_compute()

    try:
        compute.images().getFromFamily(project=project, family=family).execute()
        return True

    except HttpError as err:
        if err.resp.status == 404:
            return False
        else:
            raise err


def get_image_from_family(project, family, compute=None):
    if compute is None:
        compute = build_compute()

    return compute.images().getFromFamily(project=project, family=family).execute()


def wait_for_operation(operation_name, project, zone=None, compute=None, sleep_time=1):
    
    if compute is None:
        compute = build_compute()

    while True:
        if zone is None:
            result = compute.globalOperations().get(
                project=project,
                operation=operation_name
            ).execute()
        else:
            result = compute.zoneOperations().get(
                project=project,
                operation=operation_name,
                zone=zone
            ).execute()

        if result['status'] == 'DONE':
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(sleep_time)


def wait_for_instance_status(instance_name, project, zone, status='TERMINATED', compute=None, sleep_time=5):
    
    if compute is None:
        compute = build_compute()

    while True:
        instances = list_instances(project, zone, compute)
        if "items" in instances:
            _instance = [instance for instance in instances["items"] if instance["name"] == instance_name]
            
            if len(_instance) > 0:
                _instance = _instance[0]
                if _instance['status'] == status:
                    return _instance
        else:
            break
            
        time.sleep(sleep_time)


def name_from(x):
    return "%s-%d" % (x, time.time())


def create_image(project, image_name=None, image_familly="custom", source_image_project="ubuntu-os-cloud", source_image_family="ubuntu-1604-lts", instance_name=None, zone=None, compute=None):

    if compute is None:
        compute = build_compute()

    if image_name is None:
        image_name = name_from(image_familly)
    
    image_source =  get_image_from_family(source_image_project, source_image_family, compute)

    config = {
        'name': image_name,
        'family': image_familly,
    }
    
    if instance_name is not None:
        assert zone is not None, "You should specify a zone when creating an image from an instance"
        image_info = {'sourceDisk': "/zones/%s/disks/%s" % (zone, instance_name)}
    else:
        image_info = {"sourceImage": "projects/%s/global/images/%s" % (source_image_project, image_source['name'])}
    
    config.update(image_info)

    return compute.images().insert(project=project, body=config).execute()


def list_instances(project, zone, compute=None):
    if compute is None:
        compute = build_compute()
    return compute.instances().list(project=project, zone=zone).execute()


def create_instance(name, project, zone, compute=None, machine_type="n1-standard-1",
                    image_project="ubuntu-os-cloud", image_family="ubuntu-1604-lts",
                    startup_script_path=None, metadata_items=None, is_preemptible=False, **kargs
                   ):
 
    if compute is None:
        compute = build_compute()
    image_response = compute.images().getFromFamily(project=image_project, family=image_family).execute()
    source_disk_image = image_response['selfLink']

    machine_type = "zones/%s/machineTypes/%s" % (zone, machine_type)
    startup_script =  open(startup_script_path, "r").read() if startup_script_path else None

    items = []
    if startup_script is not None:
        items += [ {'key': 'startup-script', 'value': startup_script} ]

    if metadata_items is not None:
        items += metadata_items

    config = {
        'name': name,
        'machineType': machine_type,
        'scheduling': {
            'preemptible': is_preemptible
        },
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],
        'metadata': {
            'items': items
        }
    }
    config.update(kargs)

    return compute.instances().insert(project=project, zone=zone, body=config).execute()


def delete_instance(project, zone, name, compute=None):
    if compute is None:
        compute = build_compute()
    return compute.instances().delete(project=project, zone=zone, instance=name).execute()