import os
import subprocess

from . import env
from . import prepare


def build(**kwargs):
    prepare.prepare_code()
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
