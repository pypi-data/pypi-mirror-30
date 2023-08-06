"""
TODO: There should be a registry of some kind
and when you deploy your stream it should be written to the
registry. This can be a distributed ledger with consensus rules
for deployment.
"""
import json

from pyriver.models import Channel
from pyriver.services import stream_service


REGISTRY_FILE = "/Users/patrick/.river_registry.txt"


def lookup_stream(name):
    """ Lookup the information about a channel in the network """
    try:
        with open(REGISTRY_FILE, 'r') as f:
            streams = json.loads(f.read())
            return streams[name]
    except KeyError:
        print("No stream found with the name %s." % name)


def register_stream(stream):
    """ Register the information of this channel by broadcasting it to the network """
    with open(REGISTRY_FILE, 'r') as f:
        streams = json.loads(f.read() or "{}")
        name = stream.ochannel.name
        streams[name] = {
            "stream": stream_service.to_export_doc(stream),
            "channel": to_export_doc(stream.ochannel)
        }
    with open(REGISTRY_FILE, 'w') as f:
        f.writelines(json.dumps(streams, indent=4, sort_keys=True))


def get_or_create(channeldata):
    channel = get_by_name(channeldata["name"])
    if channel:
        return channel
    channel = Channel()
    channel.name = channeldata["name"]
    channel.host = channeldata["host"]
    channel.port = channeldata["port"]
    channel.save()
    return channel


def get_by_name(name):
    return Channel.query.filter_by(name=name).first()


def to_export_doc(channel):
    return {
        "name": channel.name,
        "host": channel.host,
        "port": channel.port
    }
