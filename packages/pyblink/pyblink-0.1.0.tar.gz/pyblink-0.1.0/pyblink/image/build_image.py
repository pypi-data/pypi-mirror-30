import os
import argparse
import logging

from pyblink.util import build_compute, is_existing_family, wait_for_operation, create_image, get_image_from_family, create_instance, wait_for_instance_status, delete_instance


def build(project, zone, family, image_name=None, source_image_project="ubuntu-os-cloud", source_image_family="ubuntu-1604-lts", compute=None, create_family_if_not_exist=True, image_startup_script_path=None):

    if (not is_existing_family(family, project)) and create_family_if_not_exist:
        logging.info("Creation of the family")
        op = create_image(project, image_name, family, source_image_project=source_image_project, source_image_family=source_image_family, compute=compute)
        wait_for_operation(op["name"], project, compute=compute)

    image = get_image_from_family(project, family, compute)
    instance_name = "tmp-%s" % image["name"]
    logging.info("Creation of a temporary instance in order to prepare the image")
    op = create_instance(
        name=instance_name,
        project=project,
        zone=zone,
        image_project=project, image_family=image["family"],
        startup_script_path=image_startup_script_path,
        compute=compute
    )
    wait_for_operation(op["name"], project, zone, compute=compute)
    wait_for_instance_status(instance_name, project, zone, status='TERMINATED', compute=compute)

    logging.info("Creation of an image from the temporary instance")
    op = create_image(project, image_name, family, instance_name=instance_name, zone=zone, compute=compute)
    wait_for_operation(op["name"], project, compute=compute)

    logging.info("Deleting the temporary instance")
    delete_instance(project, zone, instance_name, compute)


def arguments_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', required=True)
    parser.add_argument('-z', '--zone', required=True)
    parser.add_argument('-f', '--family', required=True)
    parser.add_argument('--source-image-project', default="ubuntu-os-cloud")
    parser.add_argument('--source-image-family', default="ubuntu-1604-lts")
    parser.add_argument('--startup-script-path', default=None)
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

    startup_script_path = args.startup_script_path
    if startup_script_path is None:
        startup_script_path = os.path.join(os.path.dirname(__file__), "startup_script.sh")

    compute = build_compute()
    build(
        project=args.project,
        zone=args.zone,
        family=args.family,
        source_image_project=args.source_image_project,
        source_image_family=args.source_image_family,
        compute=compute,
        image_startup_script_path=startup_script_path
    )


if __name__ == '__main__':
    main()