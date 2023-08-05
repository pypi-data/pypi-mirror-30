"""Used to import assets from CSV files"""
import csv, json, copy
from argus_cli.plugin import register_command

# Authenticate
from argus_api.helpers.authentication import with_authentication

# API calls
from argus_api.api.assets.v1.host import add_host_asset, update_host_asset, search_host_assets
from argus_api.api.customers.v1.customer import get_customer_by_shortname
from argus_api.exceptions.http import ArgusException, ObjectNotFoundException

# CLI
from argus_cli.helpers.formatting import ask, success, failure
from argus_cli.helpers.log import logging

log = logging.getLogger("plugin").getChild("assets")

def diff(a: list, b: list):
    """Returns values from 'a' not found in 'b'"""
    return list(set(a) - set(b))

@register_command(extending=('assets', 'import'))
def hosts(
        customer: str,
        file_path: str,
        map_headers: list = tuple(),
        extra_json: str = None,
        field_separator: str = " ",
        headers_on_first_line: bool = False,
        always_yes: bool = False,
        dry: bool = False
    ):
    """Imports assets from a CSV file
    
    Host assets *must* provide fields 'name' and 'ipAddresses'. If the file does not provide these fields, but have
    other names for these fields such as 'ip' and 'description', pass --map-headers ip:ipAddresses,description:name to
    map the headers to these names.

    A host may have multiple ipAddresses, these should be separated by a semicolon, like: 10.0.15.12;88.283.39.12

    Optional fields are:
        - operatingSystemCPE
        - type (SERVER or CLIENT, default: SERVER)
        - source (CVM or USER, default: USER)
        - aliases (list of aliases, separated by given field separator)
        - properties (additional properties to add to the host, formatted as JSON)
    
    You can add these fields using --extra-json type:CLIENT (to apply to all hosts), or as its
    own field in the CSV file.

    :param customer: Name of the customer to import assets for
    :param file_path: Path to the CSV file
    :param map_headers: Optional map of header names, e.g ipAddressv4:address,long_description:description
    :param field_separator: Separator used inside fields, e.g when providing multiple IP addresses or aliases. Defaults to whitespace.
    :param extra_json: Adds extra field: values to each JSON object read from CSV. Can be used to add missing fields
    :param headers_on_first_line: Whether headers should be taken from the first line in the CSV
    :param dry: If this is enabled, no modifying API calls will be made
    """

    headers = None
    
    # If headers are not on the first line of the CSV file
    # and we have a map of headers, create the header names
    # either by getting the last value of every old:new pair,
    # or just each value if there's no mapping
    if not headers_on_first_line and map_headers:
        headers = [
            header.split(":").pop() if ":" in header else header
            for header in map_headers
        ]
    
    with open(file_path) as assets_file:
        try:
            assets = [asset for asset in csv.DictReader(assets_file, delimiter=",", fieldnames=headers)]
        except UnicodeDecodeError:
            raise ValueError(
                "This file seems to be corrupt, it contains strange bytes."
                "Please check the file encoding, and try to re-save the file"
            )
    
    if not assets and headers_on_first_line and not map_headers:
        raise ValueError(
            "CSV file was empty, or contained only one row "
            "but you did not define any headers so these were "
            "thought to be headers"
        )

    # Authorize our API calls
    authorize = with_authentication()
    get_customer = authorize(get_customer_by_shortname)
    add_asset = authorize(add_host_asset)
    update_asset = authorize(update_host_asset)

    # Get the customer, and fail if none was found
    try:
        customer = get_customer(customer)
    except ObjectNotFoundException:
        raise LookupError("No customer found for %s" % customer)
    
    # Search for all existing assets with the names we found
    existing_assets = authorize(search_host_assets)(keywords=[host["name"] for host in assets if "name" in host], customerID=[customer["data"]["id"]])

    # ... and create a lookup table
    existing_assets = { asset["name"]: asset for asset in existing_assets["data"] }

    # Create or update each asset (because there is no bulk add, we do it for each asset)
    for host in assets:

        # These fields are required
        if "name" not in host or "ipAddresses" not in host:
            log.plugin(
                failure("Skipping. Required fields 'name' and 'ipAddresses' not in %s" % str(host))
            )
            continue

        host.update({
            'customerID': int(customer['data']['id']),
            'ipAddresses': host['ipAddresses'].split(field_separator),
            'properties': json.loads(host['properties']) if "properties" in host else {}
        })
        
        if extra_json:
            host.update(json.loads(extra_json))

        if host["name"] in existing_assets:
            if always_yes or ask("%s already exists, do you want to update it?" % host["name"]):
                current_asset = existing_assets[host["name"]]
                try:
                    current_ips_with_range = [ "%s/%d" % (ip["address"], ip["maskBits"]) for ip in current_asset["ipAddresses"]]
                    given_ips_with_range = [ "%s/32" % ip if "/" not in ip else ip for ip in host["ipAddresses"] ]

                    host.update({
                        "addIpAddresses": diff(given_ips_with_range, current_ips_with_range),
                        "deleteIpAddresses": diff(current_ips_with_range, given_ips_with_range)
                    })
                    
                    if "aliases" in host:
                        host.update({
                            "addAliases": diff(host["aliases"].split(field_separator), [ alias["fqdn"] for alias in current_asset["aliases"] ]),
                            "deleteAliases": diff([ alias["fqdn"] for alias in current_asset["aliases"] ], host["aliases"].split(field_separator)),
                        })

                    if "properties" in host:
                        host.update({
                            "addProperties": {
                                property: value
                                for property, value in host["properties"].items()
                                if property in diff(host["properties"].keys(), current_asset["properties"].keys())
                            },
                            "deleteProperties": diff(current_asset["properties"].keys(), host["properties"].keys())
                        })

                    if not dry:
                        update_asset(
                            existing_assets[host["name"]]["id"],
                            **{
                                field: value
                                for field, value in host.items()
                                if not field in ('ipAddresses', 'customerID', 'properties', 'aliases')
                            }
                        )
                    log.plugin(
                        success("Updated %s" % host["name"])
                    )
                except ArgusException as error:
                    log.plugin(
                        failure("Failed to update %s: %s" % (host["name"], error))
                    )
        else:
            try:
                if not dry:
                    add_asset(**host)
                log.plugin(
                    success("Created %s (%s)" % (host["name"], ", ".join(host["ipAddresses"])))
                )
            except ArgusException as error:
                log.plugin(
                    failure("Failed to create %s: %s" % (host["name"], error))
                )
        