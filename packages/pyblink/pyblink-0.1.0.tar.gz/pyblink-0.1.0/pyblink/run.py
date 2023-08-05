import argparse
import logging
import json

from pyblink.util import build_compute, create_instance, wait_for_operation, wait_for_instance_status, name_from


def run(script_path, project, zone, image_family, instance_name=None, machine_type="n1-standard-16", 
        image_project=None, compute=None, metadata_items=None, is_preemptible=True, wait_for_instance_to_finish=False):

    if image_project is None:
        image_project = project

    if instance_name is None:
        instance_name = name_from(image_family)

    op = create_instance(
        name=instance_name,
        project=project,
        zone=zone,
        image_project=image_project,
        image_family=image_family,
        machine_type=machine_type,
        startup_script_path=script_path,
        metadata_items=metadata_items,
        is_preemptible=is_preemptible,
        compute=compute
    )
    
    if wait_for_instance_to_finish:
        wait_for_operation(op["name"], project, zone, compute=compute)
        wait_for_instance_status(instance_name, project, zone, status='TERMINATED', compute=compute)


def arguments_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--script-path', required=True)
    parser.add_argument('-p', '--project', required=True)
    parser.add_argument('-z', '--zone', required=True)
    parser.add_argument('-f', '--family', required=True)
    parser.add_argument('--instance-name', default=None)
    parser.add_argument('--machine-type', default="n1-standard-1")
    parser.add_argument('--image-project', default=None)
    parser.add_argument('--metadata-items-path', default=None)
    parser.add_argument('--no-preemptible', action="store_true", default=False)
    parser.add_argument('--wait-for-instance-to-finish', action="store_true", default=False)
    parser.add_argument('--log-level', default='INFO')
    return parser


def main():

    parser = arguments_parser()
    args = parser.parse_args()

    log_cong = {
        "level": getattr(logging, args.log_level.upper()),
        "format": "%(levelname)s: %(asctime)s %(message)s"
    }
    logging.basicConfig(**log_cong)
    
    metadata_items = None if args.metadata_items_path is None else json.load(open(args.metadata_items_path))

    compute = build_compute()

    run(
        script_path=args.script_path,
        project=args.project,
        zone=args.zone,
        image_family=args.family,
        instance_name=args.instance_name,
        machine_type=args.machine_type, 
        image_project=args.image_project,
        compute=compute,
        metadata_items=metadata_items,
        is_preemptible=(not args.no_preemptible),
        wait_for_instance_to_finish=args.wait_for_instance_to_finish
    )


if __name__ == '__main__':
    main()
