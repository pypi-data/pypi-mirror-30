import os

DEPLOY_ENV = os.environ.get('DEPLOY_ENV')
if DEPLOY_ENV is None:
    raise Exception('Missing DEPLOY_ENV')
DEPLOY_ENV = DEPLOY_ENV.upper()

BITBUCKET_COMMIT = os.environ.get("BITBUCKET_COMMIT", "")
BITBUCKET_BRANCH = os.environ.get("BITBUCKET_BRANCH", "")
BITBUCKET_REPO_SLUG = os.environ.get("BITBUCKET_REPO_SLUG", "")

DOCKER_IMAGE = os.environ.get('DOCKER_IMAGE_{env}'.format(env=DEPLOY_ENV), "")

PACKAGE_PATH = "{go_path}/src/bitbucket.org/{bitbucket_repo_owner}/{bitbucket_repo_slug}".format(
    go_path=os.environ["GOPATH"], bitbucket_repo_owner=os.environ["BITBUCKET_REPO_OWNER"],
    bitbucket_repo_slug=BITBUCKET_REPO_SLUG
)
