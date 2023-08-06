import subprocess
from pyriver.services import stream_service, channel_service


def execute(args):
    # TODO: this needs to be able to use any server
    # TODO: do not force deletion/recreation of deployment and service
    # TODO: Make sure the river is created before trying to deploy it.
    schema = stream_service.get_river_json()
    stream = stream_service.get_by_name(schema["metadata"]["name"], schema["metadata"]["user"])
    if not stream:
        stream = stream_service.create(schema)
    sport = stream.port
    cport = stream.ochannel.port
    name = schema["metadata"]["name"].replace(" ", "-").lower()
    user = schema["metadata"].get("user")
    repository = schema["metadata"].get("repository", "localhost:5000")
    imagename = "%s/%s/%s" % (repository, user, name)

    subprocess.call(["docker", "push", imagename])
    subprocess.call(["kubectl", "delete", "deployment", name])
    subprocess.call(["kubectl", "run", name, "--image=%s" % imagename])
    subprocess.call(["kubectl", "delete", "service", "api"])
    subprocess.call(["kubectl", "expose", "deployment", name, "--name=%s" % name, "--type=LoadBalancer", "--port=%s" % sport])
    channel_service.register_stream(stream)
