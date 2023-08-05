import os


def dict_environ(key):
    dict_env = {}
    value = os.environ[key]
    pairs = filter(bool, value.split(','))
    for pair in pairs:
        key_value = pair.strip().split('=')
        dict_env[key_value[0].strip()] = key_value[1].strip()

    return dict_env


def array_environ(key):
    return [x.strip() for x in os.environ[key].split(',')]


DEPLOY_ENV = os.environ['DEPLOY_ENV']
DEPLOY_ENV = DEPLOY_ENV.upper()

DOCKER_IMAGE = os.environ['DOCKER_IMAGE_{env}'.format(env=DEPLOY_ENV)]

SERVICES = array_environ('SERVICES')
SERVICE_NAME_MAPPINGS = dict_environ('SERVICE_NAME_MAPPINGS')
BRANDS = array_environ('BRANDS')
BUILD_PATHS = dict_environ('BUILD_PATHS')
JOB_NAME_MAPPINGS = dict_environ('JOB_NAME_MAPPINGS')

BITBUCKET_COMMIT = os.environ["BITBUCKET_COMMIT"]
BITBUCKET_BRANCH = os.environ["BITBUCKET_BRANCH"]
BITBUCKET_REPO_SLUG = os.environ["BITBUCKET_REPO_SLUG"]

JENKINS_JOB_TOKEN = os.environ["JENKINS_JOB_TOKEN_{env}".format(
    env=DEPLOY_ENV)]
JENKINS_USER_TOKEN = os.environ["JENKINS_USER_TOKEN_{env}".format(
    env=DEPLOY_ENV)]
JENKINS_USER = os.environ["JENKINS_USER_{env}".format(env=DEPLOY_ENV)]
JENKINS_URL = os.environ["JENKINS_URL_{env}".format(env=DEPLOY_ENV)]

AWS_ACCESS_KEY_ID = os.environ[
    "AWS_ACCESS_KEY_ID_{env}".format(env=DEPLOY_ENV)]
AWS_SECRET_ACCESS_KEY = os.environ[
    "AWS_SECRET_ACCESS_KEY_{env}".format(env=DEPLOY_ENV)]
AWS_DEFAULT_REGION = os.environ[
    "AWS_DEFAULT_REGION_{env}".format(env=DEPLOY_ENV)]

'''
Set environment variables
'''
os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
os.environ["AWS_DEFAULT_REGION"] = AWS_DEFAULT_REGION

ALLOW_BRANDS_SERVICES = {}
for brand in BRANDS:
    ALLOW_BRANDS_SERVICES[brand] = {}
    for service in SERVICES:
        ALLOW_BRANDS_SERVICES[brand][service] = service

    for other_name, service_name in SERVICE_NAME_MAPPINGS.items():
        ALLOW_BRANDS_SERVICES[brand][other_name] = service_name
