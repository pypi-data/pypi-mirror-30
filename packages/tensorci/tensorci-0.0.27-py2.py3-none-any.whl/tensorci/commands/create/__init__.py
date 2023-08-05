import click
from tensorci.commands.create.dataset import dataset


@click.group()
def create():
  """
  Create a TensorCI resource.

  Currently supported resources:

  * dataset
  """
  pass


create.add_command(dataset)