import sys
import argparse
import subprocess

from . import commands
from . import message_parser
from . import env
from . import utils


def main():
    '''Setup hook function for excepthook'''
    sys.excepthook = utils.my_except_hook

    '''Setup un buffered stdout'''
    sys.stdout = utils.UnBuffered(sys.stdout)

    '''Login ecr'''
    subprocess.check_output(
        "aws ecr get-login --no-include-email", shell=True)

    subprocess.check_output(
        "eval $(aws ecr get-login --no-include-email)", shell=True)

    parser = argparse.ArgumentParser()

    language_parsers = parser.add_subparsers(dest='lang')
    setup_go_parser(language_parsers)
    setup_common_language_parser('ruby', language_parsers)
    setup_common_language_parser('scala', language_parsers)
    setup_common_language_parser('python', language_parsers)
    setup_common_language_parser('node', language_parsers)

    kwargs = vars(parser.parse_args())

    commit_msg = subprocess.check_output("git log -1 --pretty=%B {commit}".format(commit=env.BITBUCKET_COMMIT).split()) \
        .strip().decode('utf-8')

    parsed_message = message_parser.parse_message(
        commit_msg, env.BITBUCKET_COMMIT, env.ALLOW_BRANDS_SERVICES, env.JOB_NAME_MAPPINGS, env.BUILD_PATHS, env.DEPLOY_ENV)

    if kwargs['cmd'] == 'test':
        commands.test(parsed_message=parsed_message, **kwargs)
    elif kwargs['cmd'] == 'build':
        commands.build(parsed_message=parsed_message, **kwargs)
    elif kwargs['cmd'] == 'deploy':
        commands.deploy(parsed_message)


def setup_go_parser(language_parsers):
    parser = language_parsers.add_parser('go')
    cmd_parsers = parser.add_subparsers(dest='cmd')

    build_parser = cmd_parsers.add_parser('build')
    build_parser.add_argument(
        '-c', '--use-gcc', dest='use-gcc', action='store_true', help='Using GCC for building GO')

    cmd_parsers.add_parser('deploy')
    cmd_parsers.add_parser('test')


def setup_common_language_parser(lang, language_parsers):
    parser = language_parsers.add_parser(lang)
    cmd_parsers = parser.add_subparsers(dest='cmd')

    cmd_parsers.add_parser('build')
    cmd_parsers.add_parser('deploy')
    cmd_parsers.add_parser('test')


if __name__ == '__main__':
    main()
