import urllib.request
import base64
import os
import sys

from . import utils
from . import env
from . import utils


def build(lang, parsed_message, **kwargs):
    print(utils.color_string(utils.BUILD_TITLE,
                             utils.GREEN_COLOR, utils.DEFAULT_COLOR))

    if len(parsed_message.deploy_services) == 0:
        print('INGORE BUILD! NO SERVICES FOR BUILDING.')
        return

    for service in parsed_message.deploy_services.values():
        print('Start build for service : "{sc1}{s}{sc2}"\n'.format(
            sc1=utils.GREEN_COLOR, s=service['name'], sc2=utils.DEFAULT_COLOR))

        kwargs['image_tag'] = service['image_tag']
        kwargs['build_path'] = service['build_path']

        if lang == 'go':
            from .go import build
        elif lang == 'ruby':
            from .ruby import build
        elif lang == 'node':
            from .ruby import build
        elif lang == 'python':
            from .ruby import build
        elif lang == 'scala':
            from .ruby import build

        build(**kwargs)


def test(lang, parsed_message, **kwargs):
    print(utils.color_string(utils.TEST_TITLE,
                             utils.GREEN_COLOR, utils.DEFAULT_COLOR))

    if lang == 'go':
        from .go import test
    elif lang == 'ruby':
        from .ruby import test
    elif lang == 'node':
        from .ruby import test
    elif lang == 'python':
        from .ruby import test
    elif lang == 'scala':
        from .ruby import test

    test(**kwargs)


def deploy(parsed_message):
    print(utils.color_string(utils.DEPLOY_TITLE,
                             utils.GREEN_COLOR, utils.DEFAULT_COLOR))

    if parsed_message.unsupported:
        print(utils.color_string('Unsupported services for deploying',
                                 utils.MAGENTA_COLOR, utils.DEFAULT_COLOR))
        for brand, services in parsed_message.unsupported.items():
            for service in services.values():
                print(
                    '\t* Brand: "{b}", Service: "{s}"'.format(b=brand, s=service['name']))

    if len(parsed_message.deploy_services) == 0:
        print('INGORE DEPLOY! NO SERVICES FOR DEPLOYMENT.')
        return

    for service in parsed_message.deploy_services.values():
        try:
            print('Start deploy for service : "{sc1}{s}{sc2}"'.format(
                sc1=utils.GREEN_COLOR, s=service['name'], sc2=utils.DEFAULT_COLOR))

            for brand in service['brands'].values():
                print('\tDeploy for brand: "{bc1}{b}{bc2}"'.format(
                    bc1=utils.GREEN_COLOR, b=brand['name'], bc2=utils.DEFAULT_COLOR))

                trigger_jenkins(env.JENKINS_URL, env.JENKINS_USER, env.JENKINS_USER_TOKEN,
                                brand['job_name'], env.JENKINS_JOB_TOKEN, service['image_tag'])
        except:
            typ, value, tb = sys.exc_info()
            utils.my_except_hook(typ, value, tb)


def trigger_jenkins(jenkins_url, jenkins_user, jenkins_user_token, job_name, job_token, image_tag):
    """
    Trigger deploy job on Jenkins.
    """
    url = '{jenkins_url}/job/{job_name}/buildWithParameters?token={job_token}&_IMAGE_TAG={image_tag}&cause=Bitbucket+pipeline+trigger'.format(
        jenkins_url=jenkins_url, job_name=job_name, job_token=job_token, image_tag=image_tag)
    request = urllib.request.Request(url)

    basic_auth = base64.standard_b64encode("{user}:{token}".format(
        user=jenkins_user, token=jenkins_user_token).encode('utf-8'))

    request.add_header(
        "Authorization", "Basic %s" % basic_auth.decode('utf-8'))

    urllib.request.urlopen(request)
