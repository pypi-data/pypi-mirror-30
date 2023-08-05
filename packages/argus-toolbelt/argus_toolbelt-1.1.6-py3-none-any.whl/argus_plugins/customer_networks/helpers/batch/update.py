from typing import Dict, List
import json

from argus_api.api.customernetworks.v1.network import update_customer_network
from argus_api.exceptions.http import ArgusException
from argus_cli.helpers import formatting
from argus_cli.helpers.log import log
from argus_plugins.customer_networks.helpers.diff import diff_table

def update(
        networks: List['CustomerNetwork'],
        customer: Dict,
        authenticate: callable,
        dry: bool = False,
        skip_confirmation: bool = False
    ) -> List[str]:
    """Updates existing networks

    :param list networks: List of CustomerNetworks
    :param bool dry: Whether any actual changes should be performed or not
    :param bool interactive: Ask the user to continue on each network?
    :return list[str]: Summary of messages produced
    """

    # Find all networks that have changed in the given list:
    dirty_networks = [n for n in networks if n.is_dirty()]

    # This will hold our messages (failure, success, etc), which we display at the end
    summary = []

    # If we have dirty networks, and we're not running in interactive mode,
    # perform the action on all networks without asking the user for each
    # network. Only ask once, after showing the difference.
    if any(dirty_networks):

        # Print the difference table showing which networks will be
        # updated and with what new values they will be updated
        print(
            formatting.table(
              data=diff_table(dirty_networks),
              keys=("IP", "Description", "Zone", "Location", "Flags"),
              title='Changes to %s networks' % customer['name'],
            )
        )

        # Ask the user to confirm the change if we're not running with 
        # `skip_confirmation`
        if skip_confirmation or formatting.ask("Accept changes?"):
            log.info("Updating networks for %s" % customer["name"])

            for network in dirty_networks:
                log.info(
                    "Updating network %s for %s" % (
                      network.to_json()['networkAddress'],
                      customer["name"]
                    )
                )

                try:
                    # Only perform the actual update action when
                    # not running in dry mode:
                    if not dry:

                        # Update the network with its dirty
                        # (modified) fields before creating JSON
                        # from it
                        network.update(network._dirty)
                        authenticate(update_customer_network)(
                          **{
                                key: value
                                for key, value in network.to_json().items()
                                
                                # Allowed fields for update:
                                if key in (
                                    'networkID',
                                    'location',
                                    'description',
                                    'flagsToEnable',
                                    'flagsToDisable'
                                )
                            }
                        )
                    
                    # Add success message to summary report
                    summary.append(
                        "%s Network %s updated on Argus" % (
                            # Green tick-mark:
                            formatting.green("\u2713"),
                            network.to_json()['networkAddress']
                        )
                    )
                    log.debug(summary[-1])

                # If we received a HTTP error, add the error message
                # to the summary report and log an error.
                except ArgusException as error:
                    summary.append(
                      "%s Failed to update network %s on Argus: %s" % (
                        formatting.red('X'),
                        network.to_json()['networkAddress'],
                        error
                      )
                    )
                    log.error(summary[-1])
    return summary