import os, json
from typing import List, Dict

from argus_cli.plugin import register_command
from argus_cli.helpers import formatting
from argus_cli.helpers.log import log
from argus_api.exceptions.http import ArgusException
from argus_api.helpers import authentication

from argus_api.api.customers.v1.customer import get_customer_by_shortname
from argus_api.api.customernetworks.v1.network import update_customer_network, search_customer_network

from .customer_network import CustomerNetwork
from .helpers import interactive as interactive_action, batch as batch, diff


@register_command(extending="customer-networks")
def update(
  customer: str,
  file: str,
  format: str = "address,description",
  firstLineDefinesFormat: bool = False,
  alwaysYes: bool = False,
  replace: bool = False,
  interactive: bool = False,
  deleteMissing: bool = False,
  delimiter: str = ",",
  dry: bool = False,
  api_key: str = None
  ) -> None:
    """
    Update customer networks from CSV file

    :param customer: Customer shortname
    :param file: Path to CSV file
    :param format: CSV format (available fields: address, description, subnetmask, zone)
    :param firstLineDefinesFormat: If set, --format will be ignored and the CSV file is assumed to define the fields on the first line
    :param alwaysYes: Skip confirmation on updates (WARNING: If run with Replace, this will always replace existing networks, if run with Delete, networks not found in CSV will always be deleted from Argus! Use with caution.)
    :param replace: Update networks that already exist with new information
    :param deleteMissing: Remove networks on Argus if they dont exist in the file (update, create from file and remove from argus)
    :param delimiter: CSV delimiter character
    :param interactive: Performs updates interactively and requires user to confirm each change
    :param dry: Performs a dry run - no updates will be sent to Argus
    :alias file: csv
    :alias format: F
    :alias firstLineDefinesFormat: L
    :alias alwaysYes: y
    :alias replace: R
    :alias deleteMissing: X
    :alias delimiter: t
    :alias interactive: i
    :alias dry: D

    """
    authorize = authentication.with_authentication(api_key=api_key or os.environ.get("ARGUS_API_KEY"))
    
    # Find customer by name
    customer = authorize(get_customer_by_shortname)(shortName=customer)

    if not customer:
        raise LookupError('No customer has been selected. Customer is required to edit customer networks.')

    customer = customer["data"]

    # Otherwise select the only customer
    # Fetch all networks for customer
    existing_networks = authorize(search_customer_network)(
        customerID=[customer["id"]],
        limit=0
    )

    # Convert them to CustomerNetwork objects
    existing_networks = list(map(CustomerNetwork.from_json, existing_networks["data"]))

    changes = diff.diff_file_vs_argus(
        network_list=CustomerNetwork.from_csv(
            file,
            header_format=None if firstLineDefinesFormat else format.split(','),
            headers_on_first_line=firstLineDefinesFormat,
            delimiter=delimiter,
            customer=customer,
        ),
        existing_networks=existing_networks
    )

    messages = []

    if interactive:
        create = interactive_action.create
        update = interactive_action.update
        destroy = interactive_action.destroy
    else:
        create = batch.create
        update = batch.update
        destroy = batch.destroy

    
    if replace and len(changes['CHANGED_IN_FILE']):
        messages += update(
            changes['CHANGED_IN_FILE'],
            customer,
            dry=dry,
            authenticate=authorize,
            skip_confirmation=alwaysYes
        )

    if len(changes['NOT_ON_SERVER']):
        messages += create(
            changes['NOT_ON_SERVER'],
            customer,
            dry=dry,
            authenticate=authorize,
            skip_confirmation=alwaysYes
        )

    if deleteMissing and len(changes['NOT_IN_FILE']):
        messages += destroy(
            changes['NOT_IN_FILE'],
            customer,
            dry=dry,
            authenticate=authorize,
            skip_confirmation=alwaysYes
        )

    # Print summary
    if len(messages):
        formatting.clear()
        print(
            formatting.table(
              data=[{ "message": msg} for msg in messages],
              title="Summary",
              keys=["message"]
            )
        )