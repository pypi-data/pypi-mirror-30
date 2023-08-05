import os
import subprocess

from . import env
from . import prepare


def test(**kwargs):
    prepare.prepare_code()
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
