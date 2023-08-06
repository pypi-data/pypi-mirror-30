import json
import socket

from pyriver.db import db
from pyriver.models import Stream, Channel
from pyriver.services import channel_service


def create(schema):
    # TODO: Make sure you can get the proper host
    if not validate_schema(schema):
        return None
    stream = Stream()
    meta = schema['metadata']
    stream.name = meta.get('name')
    stream.description = meta.get('description')
    stream.entry_point = meta.get('entry_point')
    stream.raw_schema = json.dumps(schema)
    stream.host = "0.0.0.0"
    stream.port = 9876
    stream.user = "ptbrodie"
    channel = Channel()
    channel.name = "%s/%s" % (stream.user, stream.name)
    channel.host = "127.0.0.1"
    channel.port = 6379
    stream.ochannel = channel
    stream.ichannels = []
    if schema['data']:
        for channel in get_ichannels(schema):
            stream.ichannels.append(channel)
    stream.save()
    return stream


def get_or_create(streamdata, channel):
    stream = get_by_name(streamdata["name"], streamdata["user"])
    if stream:
        return stream
    stream = Stream()
    stream.host = streamdata["host"]
    stream.port = streamdata["port"]
    stream.user = streamdata["user"]
    stream.name = streamdata["name"]
    stream.ochannel = channel
    stream.save()


def validate_schema(schema):
    return True


def get_ichannels(schema):
    # TODO: recursive case is to return all leaves
    istreams = set()
    for k, v in schema['data'].items():
        if k == "_comment":
            continue
        istreams.add(v.split('.')[0])
    for istream in istreams:

        streamdata = channel_service.lookup_stream(istream)
        channel = channel_service.get_or_create(streamdata["channel"])
        stream = get_or_create(streamdata["stream"], channel)
        yield channel


def get_by_id(stream_id):
    return Stream.query.filter_by(id=stream_id).first()


def get_by_name(name, user):
    return Stream.query.filter_by(name=name).first()


def to_doc(stream):
    return {
        "id": stream.id,
        "name": stream.name,
        "description": stream.description,
        "links": {
            "events": "/streams/{}/events".format(stream.id),
            "info": "/streams/{}".format(stream.id)
        }
    }


def to_export_doc(stream):
    return {
        "name": stream.name,
        "port": stream.port,
        "host": stream.host,
        "user": "ptbrodie"
    }


def get_river_json(schemafile="river.json"):
    with open(schemafile, "rb") as riverfile:
        return json.load(riverfile)


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port
