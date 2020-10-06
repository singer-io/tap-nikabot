#!/usr/bin/env python3
import argparse
import pkg_resources
from datetime import datetime, timezone
from typing import Dict, Any, cast
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

        bookmark_column = selected_stream.replication_key
        replication_method = (
            ReplicationMethod[selected_stream.replication_method] if selected_stream.replication_method else None
        )
        last_bookmark = state.get(selected_stream.tap_stream_id)

        singer.write_schema(
            stream_name=selected_stream.tap_stream_id,
            schema=selected_stream.schema.to_dict(),
            key_properties=selected_stream.key_properties,
            bookmark_properties=[bookmark_column] if bookmark_column else None,
        )

        stream = streams.get(selected_stream.tap_stream_id)
        max_bookmark = last_bookmark if replication_method == ReplicationMethod.INCREMENTAL else None
        for records in stream().get_records(client, config, bookmark_column, last_bookmark, replication_method):
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
            if bookmark_column:
                if stream.replication_key_is_sorted:
                    # update bookmark to latest value
                    singer.write_state({selected_stream.tap_stream_id: records[-1][bookmark_column]})
                else:
                    local_max_bookmark = max([row[bookmark_column] for row in records])
                    # if data unsorted, save max value until end of writes
                    max_bookmark = max(max_bookmark, local_max_bookmark) if max_bookmark else local_max_bookmark
        if bookmark_column and not stream.replication_key_is_sorted:
            singer.write_state({selected_stream.tap_stream_id: max_bookmark})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version="%(prog)s v" + __version__)
    parser.parse_known_args()
    return cast(argparse.Namespace, utils.parse_args(REQUIRED_CONFIG_KEYS))


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
