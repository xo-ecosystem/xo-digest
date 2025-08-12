from invoke import task
from xo_core.handles.registry import read_record
from xo_core.handles.verify import generate_maintainer_token


@task
def token(c, handle="brie"):
    print(generate_maintainer_token())


@task
def show(c, handle="brie"):
    print(read_record(handle))
