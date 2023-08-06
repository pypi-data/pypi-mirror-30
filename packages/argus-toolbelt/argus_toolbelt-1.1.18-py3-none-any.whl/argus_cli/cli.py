from colorama import init, deinit
from pprint import pprint

from argus_api.argus import load
from argus_cli.helpers.log import log
from argus_cli import plugin, __version__
from argus_cli.arguments import get_command_arguments, get_plugin_arguments
from argus_cli.plugin import run_command, load_plugin_module, get_plugin_modules, register_command_metadata
from argus_cli.settings import settings


def setup() -> None:
    """Does setup of the API and loads plugins"""
    plugin.api = load()
    plugins = get_plugin_modules(settings["cli"]["plugins"])
    log.info("Loading plugins...")
    for plug in plugins:
        load_plugin_module(plug)


def run() -> None:
    """Parses command and runs the application"""
    plugin_name, command_name = get_plugin_arguments()
    register_command_metadata(plugin_name, command_name)

    arguments = get_command_arguments()

    # If the plugin returned something, pretty print it (useful for API plugins)
    result = run_command(plugin_name, command_name, arguments)

    if result:
        pprint(result)


def main() -> None:
    """Used to launch the application"""
    # Initialize colorama to enable Windows color support
    init()
    setup()
    run()

    # Deinitialize colorama
    deinit()
