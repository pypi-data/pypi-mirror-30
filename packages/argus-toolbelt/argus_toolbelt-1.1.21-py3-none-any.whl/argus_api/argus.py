"""Provides the wrapper class for Argus API"""
from os import mkdir, getenv
from os.path import dirname, join, abspath, exists
from types import ModuleType
from datetime import datetime
from requests.exceptions import SSLError, Timeout, ProxyError
import ssl
from urllib3.exceptions import MaxRetryError

from argus_api.helpers.log import log
from argus_api.helpers.module_loader import import_submodules
from argus_api.parsers import openapi2
from argus_api.helpers.generator import write_endpoints_to_disk

DEFAULT_API_DIRECTORY = join(abspath(dirname(__file__)), "api")


def regenerate_api(schema_uri: str, parser: ModuleType = None):
    """Regenerates the API into the default location

    :param parser: Parser to parse the definitions with
    :param str schema_uri: Path or URL to schema
    """
    parser = parser or openapi2
    
    try:
        log.info("Generating API modules using %s..." % schema_uri)
        endpoints = parser.load(schema_uri)
        log.info("Creating module directory...")
        if not exists(DEFAULT_API_DIRECTORY):
            mkdir(DEFAULT_API_DIRECTORY)

        log.info("Writing API modules to disk...")
        write_endpoints_to_disk(
            endpoints,
            output=DEFAULT_API_DIRECTORY,
            with_plugin_decorators=True
        )
    except (SSLError, Timeout, ProxyError, MaxRetryError, ssl.SSLError) as error:
        log.error(error)
        log.error("Please check that REQUESTS_CA_BUNDLE is set to the correct certificate if you're behind an SSL terminating proxy.")
        log.error("REQUESTS_CA_BUNDLE=%s" % getenv('REQUESTS_CA_BUNDLE'))
        exit(1)


def load(api_url: str, swagger_files: list, parser: ModuleType = None, **kwargs) -> ModuleType:
    """Initializes the ArgusAPI, so that when called, the static API files will
    be generated to disk if they dont already exist, and the module then returned
    to the user. If the api module already exists, return the loaded module.

    :param api_url:
    :param swagger_files: Swagger files to load from the given api UPL
    :param base_url: Base URL to fetch the schema
    :param parser: Optional custom parser module for parsing the schema before writing to disk
    """

    # Attempt to load module api. This module doesn't exist by default,
    # and so on first run, this module will be generated
    parser = parser or openapi2
    
    try:
        import argus_api.api

        # If the time of generation is older than 2 days,
        # force regeneration
        time_ago = (datetime.now() - datetime.fromtimestamp(argus_api.api.__CREATED_AT__))
        if time_ago.days > 1:
            log.info("Argus API files are %d days old. Re-generating..." % time_ago.days)
            raise ImportError

    except ImportError:
        log.info("No static API files found. Generating them...")
        for schema in swagger_files:
            regenerate_api("%s%s" % (api_url, schema), parser)
            
    # DONT swallow other exceptions! 
    except Exception as error:
        log.error(error)
        exit(1)
    
    import argus_api.api
    import_submodules("argus_api.api", exclude_name="test_helpers")
    return argus_api.api
