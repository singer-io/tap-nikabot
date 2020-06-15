#!/usr/bin/env python3
from functools import partial
import singer
from singer import utils
from singer.catalog import Catalog
from .streams import user
from . import client


LOGGER = singer.get_logger()
BASE_URL = "https://api.nikabot.com"
DEFAULT_CONFIG = {"page_size": 1000}
REQUIRED_CONFIG_KEYS = ["access_token"]


def discover():
    swagger = client.fetch_swagger_definition(BASE_URL)
    schemas = [user.get_schema(swagger)]
    return Catalog(schemas)


def sync(config, state, catalog):
    """ Sync data from tap source """
    session = client.make_session(config["access_token"])
    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream: %s", stream.tap_stream_id)

        bookmark_column = stream.replication_key
        is_sorted = False

        singer.write_schema(
            stream_name=stream.tap_stream_id, schema=stream.schema.to_dict(), key_properties=stream.key_properties,
        )

        max_bookmark = ""
        fetch_users = partial(client.fetch_users, BASE_URL, session, config["page_size"])
        for rows in user.get_records(fetch_users):
            # write one or more rows to the stream:
            singer.write_records(stream.tap_stream_id, rows)
            if bookmark_column:
                if is_sorted:
                    # update bookmark to latest value
                    singer.write_state({stream.tap_stream_id: rows[-1][bookmark_column]})
                else:
                    # if data unsorted, save max value until end of writes
                    max_bookmark = max(max_bookmark, max([row[bookmark_column] for row in rows]))
        if bookmark_column and not is_sorted:
            singer.write_state({stream.tap_stream_id: max_bookmark})


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
