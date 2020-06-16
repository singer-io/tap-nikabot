#!/usr/bin/env python3
import singer
from singer import utils
from singer.catalog import Catalog
from .streams import all_streams
from .client import Client

LOGGER = singer.get_logger()
DEFAULT_CONFIG = {"page_size": 1000}
REQUIRED_CONFIG_KEYS = ["access_token"]


def discover():
    swagger = Client.fetch_swagger_definition()
    schemas = [stream.get_schema(swagger) for stream in all_streams]
    return Catalog(schemas)


def sync(config, state, catalog):
    """ Sync data from tap source """
    client = Client(config["access_token"], config["page_size"])
    # Loop over selected streams in catalog
    for selected_stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream: %s", selected_stream.tap_stream_id)

        bookmark_column = selected_stream.replication_key
        is_sorted = False

        singer.write_schema(
            stream_name=selected_stream.tap_stream_id,
            schema=selected_stream.schema.to_dict(),
            key_properties=selected_stream.key_properties,
        )

        max_bookmark = ""
        stream = next(s for s in all_streams if s.STREAM_ID == selected_stream.tap_stream_id)
        for rows in stream.get_records(client):
            # write one or more rows to the stream:
            singer.write_records(selected_stream.tap_stream_id, rows)
            if bookmark_column:
                if is_sorted:
                    # update bookmark to latest value
                    singer.write_state({selected_stream.tap_stream_id: rows[-1][bookmark_column]})
                else:
                    # if data unsorted, save max value until end of writes
                    max_bookmark = max(max_bookmark, max([row[bookmark_column] for row in rows]))
        if bookmark_column and not is_sorted:
            singer.write_state({selected_stream.tap_stream_id: max_bookmark})


@utils.handle_top_exception(LOGGER)
def main():
    # Parse command line arguments
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
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
