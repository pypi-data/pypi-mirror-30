import subprocess
import re


class ParsedMessage(object):
    def __init__(self):
        """Return a new ParsedMessage"""
        self.deploy_brands = {}
        self.deploy_services = {}
        self.unsupported = {}

    def is_deploy(self):
        return bool(self.deploy_brands)


def parse_message(message, commit_hash, allow_brands_services, job_name_mappings, build_paths, deploy_env):
    parsed_message = ParsedMessage()

    if len(allow_brands_services) == 1:
        if len(next(iter(allow_brands_services.values()))) == 1:
            if re.match(r"\[deploy\]", message):
                parsed_message.is_push_image = True
            else:
                parsed_message.is_push_image = False

            brand_name = next(iter(allow_brands_services.keys()))
            brand = next(iter(allow_brands_services.values()))
            service = next(iter(brand.values()))
            message = "[deploy_{b}_{s}]".format(
                b=brand_name, s=service) + message
        else:
            match_tags = re.finditer(r"\[deploy_([^\_[]*)\]", message)
            brand_name = next(iter(allow_brands_services.keys()))
            for _, match in enumerate(match_tags):
                service = match.group(1)
                message = "[deploy_{b}_{s}]".format(
                    b=brand_name, s=service) + message

    match_tags = re.finditer(r"\[deploy_([^\_[]*)_([^\_[]*)\]", message)

    for _, match in enumerate(match_tags):
        brand = match.group(1)
        service = match.group(2)

        if brand in allow_brands_services and service == 'all':
            if brand not in parsed_message.deploy_brands:
                parsed_message.deploy_brands[brand] = {}

            for _, v in allow_brands_services[brand].items():
                parsed_message.deploy_brands[brand][v] = {'name': v}

            continue

        if brand in allow_brands_services and service in allow_brands_services[brand]:
            if brand not in parsed_message.deploy_brands:
                parsed_message.deploy_brands[brand] = {}

            parsed_message.deploy_brands[brand][allow_brands_services[brand]
                                                [service]] = {'name': allow_brands_services[brand][service]}
        else:
            if brand not in parsed_message.unsupported:
                parsed_message.unsupported[brand] = {}

            parsed_message.unsupported[brand][service] = {
                'name': service}

    for brand, services in parsed_message.deploy_brands.items():
        for _, service in services.items():
            job_name = '{b}-{s}'.format(b=brand, s=service['name'])
            if job_name in job_name_mappings:
                job_name = job_name_mappings[job_name]
            service['job_name'] = '{e}-{n}'.format(e=deploy_env, n=job_name)

            build_path = ""
            if service['name'] in build_paths:
                build_path = build_paths[service['name']]
            service['build_path'] = build_path

            service['image_tag'] = '{s}-{h}'.format(
                s=service['name'], h=commit_hash)

    for brand, services in parsed_message.deploy_brands.items():
        for service_name, service in services.items():
            if service_name not in parsed_message.deploy_services:
                parsed_message.deploy_services[service_name] = {
                    'name': service['name'],
                    'build_path': service['build_path'],
                    'image_tag': service['image_tag'],
                }
                parsed_message.deploy_services[service_name]['brands'] = {}

            parsed_message.deploy_services[service_name]['brands'][brand] = {
                'name': brand, 'job_name': service['job_name']}

    return parsed_message
