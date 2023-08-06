import argparse
import logging
import os
import subprocess
import sys

import docker
from streamsets.sdk.config import USER_CONFIG_PATH
from streamsets.sdk.exceptions import ActivationError
from streamsets.sdk.sdc_api import ACTIVATION_FILE_NAME

DEFAULT_DOCKER_IMAGE = 'streamsets/testframework:master'
DEFAULT_DOCKER_NETWORK = 'cluster'

DEFAULT_TESTFRAMEWORK_CONFIG_DIRECTORY = os.path.expanduser('~/.streamsets/testframework')

DEFAULT_BUILD_NAME = 'latest'
DEFAULT_BUILD_S3_BUCKET = 'nightly.streamsets.com'
DEFAULT_BUILD_DOCKER_REPO = 'streamsets/datacollector-libs'

logger = logging.getLogger('streamsets.testframework.cli')


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', help='Be noisier')
    parser.add_argument('--docker-image',
                        metavar='image',
                        help='Docker image to use for the STF container',
                        default=DEFAULT_DOCKER_IMAGE)
    parser.add_argument('--docker-image-dont-pull',
                        action='store_true',
                        help="Don't pull STF Docker image")
    parser.add_argument('--docker-network',
                        metavar='network',
                        help='Docker network to which to attach the STF container',
                        default=DEFAULT_DOCKER_NETWORK)
    parser.add_argument('--testframework-config-directory',
                        metavar='dir',
                        help=("A directory containing STF configuration files to mount into the "
                              "STF container"),
                        default=DEFAULT_TESTFRAMEWORK_CONFIG_DIRECTORY)
    parser.add_argument('--testframework-directory',
                        metavar='dir',
                        help=("A testframework directory to mount into the STF container (for use "
                              "when making STF changes that don't really a rebuild of the image)"))
    subparsers = parser.add_subparsers(help='Test Framework subcommands', dest='subcommand')

    test_subparser = subparsers.add_parser('test', help='Run STF tests', add_help=False)
    test_subparser.add_argument('test_command', metavar='<test command>',
                                help='Arguments to pass to our test execution framework',
                                nargs=argparse.REMAINDER)

    # shell_subparser = subparsers.add_parser('shell', help='Open a shell within the STF container')

    build_subparser = subparsers.add_parser('build',
                                            help='Build STF Docker images',
                                            add_help=False)
    build_subparser.add_argument('build_command', metavar='<build command>',
                                 help='Arguments to pass to the image build script',
                                 nargs=argparse.REMAINDER)

    args, unknown = parser.parse_known_args()

    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)

    client = docker.from_env()

    if not args.docker_image_dont_pull:
        logger.info('Pulling Docker image %s ...', args.docker_image)
        client.images.pull(args.docker_image)

    _create_docker_network(client, args.docker_network)

    container_hostname = _get_stf_container_hostname(client)

    environment = {
        'TESTFRAMEWORK_CONFIG_DIRECTORY': args.testframework_config_directory,
    }
    # TODO: Move the AWS and Azure environment variables into
    #       an ini file.
    for variable in ('AWS_ACCESS_KEY_ID',
                     'AWS_SECRET_ACCESS_KEY',
                     'azure_tenant_id',
                     'azure_client_id',
                     'azure_client_secret',
                     'azure_storage_account_key',
                     'azure_storage_account_name',
                     'azure_eh_sas_connection_primary',
                     'azure_iot_sas_connection_primary',
                     'azure_sb_sas_connection_primary'):
        environment[variable] = os.getenv(variable)

    user_activation_file_path = os.path.join(USER_CONFIG_PATH, 'activation', ACTIVATION_FILE_NAME)
    if not os.path.isfile(user_activation_file_path):
        raise ActivationError('Could not find activation file at {}'.format(user_activation_file_path))
    stf_container_activation_file_path = os.path.join('/root/.streamsets/activation', ACTIVATION_FILE_NAME)

    container_configs = {
        'auto_remove': False,
        'detach': True,
        'environment': environment,
        'hostname': container_hostname,
        'network': args.docker_network,
        'volumes': {os.getcwd(): dict(bind='/root/tests', mode='rw'),
                    user_activation_file_path: dict(bind=stf_container_activation_file_path, mode='ro'),
                    '/var/run/docker.sock': dict(bind='/var/run/docker.sock', mode='rw'),
                    os.path.expanduser('~/.docker'): dict(bind='/root/.docker', mode='rw')},
        'tty': True,
        'working_dir': '/root/tests',
    }

    if args.subcommand == 'shell':
        raise NotImplementedError('Not ready yet ...')
    elif args.subcommand == 'test':
        logger.info('Running STF tests ...')
        test_index = sys.argv.index('test')
        command = 'pytest {}'.format(' '.join('"{}"'.format(arg) for arg in sys.argv[test_index+1:]))
        container = client.containers.run(args.docker_image, command, **container_configs)
        logger.debug('Running command (%s) in STF container (%s) ...', command, container.id)
        for line in container.attach(stream=True):
            sys.stdout.write(line.decode())
    elif args.subcommand == 'build':
        logger.info('Building STF Docker images ...')
        build_index = sys.argv.index('build')
        build_commands = (['-v'] if args.verbose else []) + sys.argv[build_index+1:]
        command = ('python3 /root/testframework/streamsets/testframework/cli/build.py {}'.format(
            ' '.join('"{}"'.format(arg) for arg in build_commands))
        )
        container = client.containers.run(args.docker_image, command, **container_configs)
        logger.debug('Running command (%s) in STF container (%s) ...', command, container.id)
        for line in container.attach(stream=True):
            sys.stdout.write(line.decode())


def _create_docker_network(client, name):
    try:
        client.networks.create(name=name, check_duplicate=True)
        logger.debug('Successfully created network (%s).', name)
    except docker.errors.APIError as api_error:
        if api_error.explanation == 'network with name {} already exists'.format(name):
            logger.warning('Network (%s) already exists. Continuing without creating ...',
                           name)
        else:
            raise


def _get_stf_container_hostname(client):
    # We set the STF container's hostname to match the host's to make the experience of running
    # tests as seamless as if they were being run from the host itself.

    # We need special logic to check whether Docker for Mac is being used and then handling
    # how it exposes ports to 'localhost'.
    docker_hostname = client.info()['Name']
    logger.debug('Docker detected hostname: %s', docker_hostname)

    hostname = subprocess.check_output('hostname', shell=True, universal_newlines=True).strip()
    logger.debug('Shell detected hostname: %s', hostname)

    if docker_hostname == hostname:
        return subprocess.check_output('hostname -f', shell=True, universal_newlines=True).strip()
    elif docker_hostname == 'moby':
        return 'localhost'
