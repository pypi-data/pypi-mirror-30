# Copyright 2017 StreamSets Inc.

import argparse
import io
import logging
import re
import subprocess
import sys
from collections import namedtuple
from itertools import chain
from pathlib import Path

import boto3
import javaproperties
from botocore.handlers import disable_signing

DEFAULT_S3_BUCKET = 'nightly.streamsets.com'
DEFAULT_BUILD = 'latest'
DEFAULT_BUILD_PREFIX = 'datacollector'
DEFAULT_BUILD_SUFFIX = 'tarball'
DEFAULT_DOCKER_REPO = 'streamsets/datacollector-libs'
DEFAULT_LEGACY_BUILD_SUFFIX = 'legacy'
DEFAULT_SDC_DOCKER_REPO_URL = 'https://github.com/streamsets/datacollector-docker.git'
DEFAULT_STAGE_LIB_MANIFEST_FILENAME = 'stage-lib-manifest.properties'
DEFAULT_STAGE_LIBRARIES_DIRECTORY_PATH = Path('/root/testframework/streamsets/testframework/libraries/stage')
DEFAULT_BUILD_ARGS = []

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
                                       '%Y-%m-%d %I:%M:%S %p'))
logger = logging.getLogger('streamsets.testframework.cli.build')
logger.addHandler(handler)

# Use a namedtuple to maintain all the information needed to build one of our Docker images.
DockerImage = namedtuple('DockerImage', ['image_name', 'dockerfile_path', 'build_args'])


def main():
    """Main function invoked from command line."""
    parser = argparse.ArgumentParser(
        prog='stf build',
        description='Build the Docker images used by the StreamSets Test Framework',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-v', '--verbose', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--s3-bucket',
                        help='S3 bucket to get tarballs from',
                        default=DEFAULT_S3_BUCKET)
    parser.add_argument('--build',
                        help='The build to use from S3 (e.g. of the form "2038," "2.4," "latest")',
                        default=DEFAULT_BUILD)
    parser.add_argument('--use-aws-credentials',
                        help='If set, use local AWS credentials when communicating with Amazon S3',
                        action='store_true')
    parser.add_argument('--dry-run',
                        help="Don't actually do the `docker build`",
                        action='store_true')
    parser.add_argument('--sdc-version-tag',
                        help='A tag to use for images instead of the SDC version gleamed from '
                             'stage-lib-manifest.properties',
                        metavar='tag')
    parser.add_argument('--stage-library',
                        help='Stage library to build; can be invoked multiple times to specify several, '
                             'but will default to selecting all available stage libraries if omitted',
                        action='append')
    parser.add_argument('--push',
                        help='Push Docker images after building',
                        action='store_true')
    parser.add_argument('--build-arg',
                        help='Build argument to pass to docker build command',
                        action='append',
                        default=DEFAULT_BUILD_ARGS)
    parser.add_argument('target',
                        choices=['stage-libraries', 'extras', 'environments', 'sdc'],
                        help='Target to build')

    args = parser.parse_args()
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    if args.dry_run:
        logger.info('Doing dry-run of tool...')

    bucket = _get_s3_bucket(args)

    # Stage libs can be current or legacy. To handle the latter case, we compose both possibilities,
    # looking for tarballs at the former location first.
    key_prefix = '/'.join((DEFAULT_BUILD_PREFIX, args.build, DEFAULT_BUILD_SUFFIX))
    legacy_key_prefix = '/'.join((DEFAULT_BUILD_PREFIX, args.build, DEFAULT_LEGACY_BUILD_SUFFIX))

    sdc_version = _get_sdc_version(bucket=bucket, key_prefix=key_prefix)
    logger.info('This will build images for SDC %s...', sdc_version)

    images = []
    if args.target == 'stage-libraries':
        for object_ in chain(bucket.objects.filter(Prefix=key_prefix),
                             bucket.objects.filter(Prefix=legacy_key_prefix)):
            if object_.key.endswith(f'-lib-{sdc_version}.tgz'):
                key_match = re.search(f'{key_prefix}/(.*)-{sdc_version}.tgz', object_.key)
                legacy_key_match = re.search(f'{legacy_key_prefix}/(.*)-{sdc_version}.tgz', object_.key)
                is_legacy_stage_lib = bool(legacy_key_match)
                stage_lib_name = (key_match or legacy_key_match).group(1)

                image_name = f'{DEFAULT_DOCKER_REPO}:{stage_lib_name}-{args.sdc_version_tag or sdc_version}'
                tarball_url = _get_s3_object_url(bucket, object_.key)

                build_args = dict(
                    STAGE_LIB_ROOT=('/opt/streamsets-datacollector-user-libs'
                                    if is_legacy_stage_lib
                                    else '/opt'),
                    STAGE_LIB_DIRECTORY=(f'/opt/streamsets-datacollector-user-libs/{stage_lib_name}'
                                         if is_legacy_stage_lib
                                         else f'/opt/streamsets-datacollector-{sdc_version}/streamsets-libs/'),
                    STAGE_LIB_URL=tarball_url,
                    **{build_arg.split('=')[0]: build_arg.split('=')[1]
                       for build_arg in args.build_arg}
                )

                if not args.stage_library or stage_lib_name in args.stage_library:
                    images.append(DockerImage(image_name=image_name,
                                              dockerfile_path=DEFAULT_STAGE_LIBRARIES_DIRECTORY_PATH,
                                              build_args=build_args))
    elif args.target == 'sdc':
        build_args = dict(
            SDC_URL=_get_s3_object_url(bucket, f'{key_prefix}/streamsets-datacollector-core-{sdc_version}.tgz'),
            SDC_VERSION=sdc_version,
            **{build_arg.split('=')[0]: build_arg.split('=')[1]
               for build_arg in args.build_arg}
        )
        images.append(DockerImage(
            image_name=f'streamsets/datacollector:{args.sdc_version_tag or sdc_version}',
            dockerfile_path=DEFAULT_SDC_DOCKER_REPO_URL,
            build_args=build_args
        ))

    images_with_build_errors = build_images(images=images,
                                            dry_run=args.dry_run)

    images_with_push_errors = (push_images(set(image.image_name for image in images)
                                           - images_with_build_errors,
                                           dry_run=args.dry_run)
                               if args.push
                               else set())

    images_without_errors = (set(image.image_name for image in images)
                             - images_with_build_errors
                             - images_with_push_errors)

    if images_without_errors:
        logger.info('%s images were successfully created:\n%s',
                    len(images_without_errors),
                    '\n'.join('* {0}'.format(image) for image in sorted(images_without_errors)))

    if images_with_build_errors:
        logger.error('%s images had build errors:\n%s',
                     len(images_with_build_errors),
                     '\n'.join('* {0}'.format(image) for image in sorted(images_with_build_errors)))

    if images_with_push_errors:
        logger.error('%s images had push errors:\n%s',
                     len(images_with_push_errors),
                     '\n'.join('* {0}'.format(image) for image in sorted(images_with_push_errors)))

    if images_with_build_errors or images_with_push_errors:
        sys.exit(1)


def build_images(images, dry_run):
    """Do the actual building of Docker images.

    Args:
        images (:obj:`list`): List of DockerImage namedtuples.
        dry_run (:obj:`bool`): If ``True``, don't actually execute Docker commands (but display what they are).

    Returns:
        (:obj:`set`): A set of images with build errors.
    """
    # To handle any errors during the `docker build`, keep a set. This will also be used to exclude
    # images from being pushed if this script is run with --push.
    images_with_build_errors = set()

    for image in sorted(images):
        try:
            cmd = (f'docker build --no-cache -t {image.image_name} '
                   + ' '.join(f'--build-arg {key}={value}' for key, value in image.build_args.items())
                   + f' {image.dockerfile_path}')
            logger.debug('Running Docker build command (%s)...', cmd)
            if not dry_run:
                subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError:
            logger.error('Non-zero exit code seen while building %s...',
                         image.image_name)
            images_with_build_errors.add(image.image_name)
    return images_with_build_errors


def push_images(images, dry_run):
    """Push Docker images
    Args:
        images (:obj:`set`): Docker images to push.
        dry_run (:obj:`bool`): If ``True``, don't actually execute Docker commands (but display what they are).
    Returns:
        (:obj:`set`): A set of images with push errors.
    """
    images_with_push_errors = set()
    # Iterate over every successfully-built image (i.e. all images except those that show up in
    # the build errors list).
    logger.info('Beginning `docker push` of successfully-built images...')
    for image in sorted(images):
        try:
            cmd = f'docker push {image}'
            logger.debug('Running Docker push command (%s)...', cmd)
            if not dry_run:
                subprocess.run(cmd,
                               shell=True,
                               check=True)
        except subprocess.CalledProcessError:
            logger.error('Non-zero exit code seen while pushing %s...', image)
            images_with_push_errors.add(image)

    return images_with_push_errors


def _get_s3_bucket(args):
    """Return an S3.Bucket instance."""
    s3_resource = boto3.resource('s3')
    # In general, the S3 buckets hosting our public-facing artifacts can be accessed in anonymous mode, so
    # disable signing for our S3 client unless otherwise specified.
    if not args.use_aws_credentials:
        s3_resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
    return s3_resource.Bucket(args.s3_bucket)


def _get_s3_object_url(bucket, key):
    """Return a string of the public URL of an S3 object."""
    # Following AWS's conventions for accessing virtual-hosted-style URLs (see
    # http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html#access-bucket-intro).
    return 'http://{bucket}.s3.amazonaws.com/{key}'.format(bucket=bucket.name,
                                                           key=key) if _s3_key_exists(bucket, key) else None


def _get_sdc_version(bucket, key_prefix):
    """Parse the stage lib manifest properties file to determine the SDC version corresponding to
    this build.
    """

    # Instead of dealing with temporary files, just use Bucket.download_fileobj to copy the contents
    # of the manifest file to a BytesIO instance, which we need to read and decode before parsing.
    fileobj = io.BytesIO()
    manifest_key = '/'.join((key_prefix, DEFAULT_STAGE_LIB_MANIFEST_FILENAME))
    logger.info('Getting stage-lib-manifest.properties file (%s)...', manifest_key)
    bucket.download_fileobj(manifest_key, fileobj)
    fileobj.seek(0)

    # Each manifest has a 'version=...' line, which is all we care to parse out.
    return javaproperties.load(fileobj)['version']


def _s3_key_exists(bucket, key):
    """Return whether the given key exists in the bucket."""
    try:
        return next(iter(bucket.objects.filter(Prefix=key))).key == key
    except StopIteration:
        return False


if __name__ == '__main__':
    main()
