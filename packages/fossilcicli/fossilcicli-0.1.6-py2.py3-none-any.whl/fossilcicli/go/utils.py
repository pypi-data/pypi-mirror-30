import subprocess
import os

from . import env
from . import utils


def prepare_code():
    subprocess.check_output(
        'git config --global url."git@bitbucket.org:".insteadOf "https://bitbucket.org/"', shell=True)
    subprocess.check_output(
        'mkdir -pv "{p}"'.format(p=env.PACKAGE_PATH), shell=True)
    subprocess.check_output(
        'tar -cO --exclude=bitbucket-pipelines.yml . | tar -xv -C "{p}"'.format(p=env.PACKAGE_PATH), shell=True)

    os.chdir(env.PACKAGE_PATH)

    print("\nInstall the project's dependencies")
    subprocess.run("dep ensure -v", shell=True)

    print("\nGenerate code")
    subprocess.check_output(
        "go get bitbucket.org/misfitwearablesinc/common-lib/odm/modm/cmd/modm", shell=True)
    subprocess.check_output(
        "go install bitbucket.org/misfitwearablesinc/common-lib/odm/modm/cmd/modm", shell=True)
    subprocess.check_output("go generate ./...", shell=True)
