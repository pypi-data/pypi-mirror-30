from typing import Dict, List
import json

from argus_api.api.customernetworks.v1.network import delete_customer_network
from argus_api.exceptions.http import ArgusException
from argus_cli.helpers import formatting
from argus_cli.helpers.log import log
from argus_plugins.customer_networks.helpers.diff import diff_table



def destroy(
        networks: List['CustomerNetwork'],
        customer: Dict,
        authenticate: callable,
        dry: bool = False,
        skip_confirmation: bool = False
    ) -> List[str]:
    """Destroys existing networks

    :param list networks: List of CustomerNetworks
    :param dict customer: Customer object (used only for logging)
    :param callable authenticate: Authentication method to pass in authentication headers to API functions
    :param bool interactive: Whether or not to ask the user for each network. Defaults to asking once only.
    :returns: List of messages for summary report
    """
    # Print updates and let user accept before performing updates
    summary = []

    # Print a table of the networks that will be destroyed:
    print(
        formatting.table(
            data=networks,
            keys=("IP", "Description", "Zone", "Location", "Flags"),
            title='Remove networks for %s' % customer['name'],
            format=formatting.red
        )
    )

    # Ask the user to confirm the change unless we're running with
    # skip_confirmation (alwaysYes option)
    if skip_confirmation or formatting.ask('Accept changes?'):
        log.info("Removing networks for %s" % customer["name"])

        for network in networks:
            log.info(
                "Removing network %s for %s" % (
                    network.to_json()['networkAddress'],
                    customer["name"]
                )
            )

            try:

                # Only perform the API action if we're not running in dry
                # mode, in which case no changes will be pushed to Argus
                if not dry:
                    authenticate(delete_customer_network)(id=network['id'])

                # Add a success message to the summary report
                summary.append(
                    "%s Network %s removed from Argus" % (
                        formatting.green("\u2713"),
                        network.to_json()['networkAddress']
                    )
                )
                log.info(summary[-1])

            # Catch any error messages from the API and add them to the summary
            # report instead of crashing
            except ArgusException as error:
                summary.append(
                    "%s Failed to remove network %s from Argus: %s" % (
                        formatting.red('X'),
                        network.to_json()['networkAddress'],
                        error
                    )
                )
                log.error(summary[-1])

    return summary