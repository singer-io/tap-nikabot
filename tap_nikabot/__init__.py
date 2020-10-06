#!/usr/bin/env python3
import argparse
import pkg_resources
from datetime import datetime, timezone
from typing import Dict, Any
import singer
from singer import utils, Transformer, metadata
from singer.catalog import Catalog

from .replication_method import ReplicationMethod
from . import streams
from .client import Client

LOGGER = singer.get_logger()
DEFAULT_CONFIG = {"page_size": 1000}
REQUIRED_CONFIG_KEYS = ["access_token"]


try:
    __version__ = pkg_resources.get_distribution("tap-nikabot").version
except pkg_resources.DistributionNotFound:
    __version__ = "0.0.0"


def discover() -> Catalog:
    swagger = Client.fetch_swagger_definition()
    schemas = [stream().get_catalog_entry(swagger) for stream in streams.all_streams]
    return Catalog(schemas)


def sync(config: Dict[str, Any], state: Dict[str, Any], catalog: Catalog) -> None:
    """ Sync data from tap source """
    client = Client(config["access_token"], config["page_size"])
    # Loop over selected streams in catalog
    for selected_stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream: %s", selected_stream.tap_stream_id)

        singer.write_schema(
            stream_name=selected_stream.tap_stream_id,
            schema=selected_stream.schema.to_dict(),
            key_properties=selected_stream.key_properties,
        )

        stream = streams.get(selected_stream.tap_stream_id)
        for records in stream().get_records(client, config, replication_method=ReplicationMethod.FULL_TABLE):
            if len(records) == 0:
                continue
            # write one or more rows to the stream:
            with Transformer() as transformer:
                for record in records:
                    singer.write_record(
                        selected_stream.tap_stream_id,
                        transformer.transform(
                            record, selected_stream.schema.to_dict(), metadata.to_map(selected_stream.metadata),
                        ),
                        time_extracted=datetime.now(timezone.utc),
                    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version="%(prog)s v" + __version__)
    parser.parse_known_args()
    return utils.parse_args(REQUIRED_CONFIG_KEYS)


@utils.handle_top_exception(LOGGER)
def main() -> None:
    args = parse_args()
    config = dict(DEFAULT_CONFIG, **args.config)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover()
        catalog.dump()
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = discover()
        sync(config, args.state, catalog)


if __name__ == "__main__":
    main()
