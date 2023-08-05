import os
import subprocess

from . import env
from . import utils


def test(**kwargs):
    utils.prepare_code()
    os.chdir(env.PACKAGE_PATH)
    os.environ["ENV"] = "test"

    f = open("{go_path}/.richstyle".format(go_path=os.environ["GOPATH"]), "w")
    f.write("""startStyle:
    foreground: yellow

skipStyle:
    foreground: #0052cc""")
    f.close()

    try:
        subprocess.run(
            'RICHGO_FORCE_COLOR=1 richgo test ./... -v -cover', shell=True)

    except subprocess.CalledProcessError as e:
        print(e.output)
        exit(1)


def build(**kwargs):
    utils.prepare_code()
    os.chdir(env.PACKAGE_PATH + '/' + kwargs['build_path'])

    if not kwargs['use-gcc']:
        os.environ["CGO_ENABLED"] = "0"
        os.environ["GOOS"] = "linux"

    print("\nCompile GO")
    subprocess.run('go build -o application', shell=True)

    print('\nBuild docker image')
    subprocess.run('docker build -t {image}:{tag} .'.format(
        image=env.DOCKER_IMAGE, tag=kwargs['image_tag']), shell=True)

    print('\nPush docker image to ECR')
    subprocess.run('docker push {image}:{tag}'.format(
        image=env.DOCKER_IMAGE, tag=kwargs['image_tag']), shell=True)

    return True
