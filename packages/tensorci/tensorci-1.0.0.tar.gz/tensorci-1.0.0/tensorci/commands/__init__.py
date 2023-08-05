from tensorci.commands.create import create
from tensorci.commands.dash import dash
from tensorci.commands.get import get
from tensorci.commands.init import init
from tensorci.commands.login import login
from tensorci.commands.logout import logout
from tensorci.commands.logs import logs
from tensorci.commands.push import push
from tensorci.commands.serve import serve
from tensorci.commands.train import train
from tensorci.commands.version import version

all_cmds = [
  create,
  dash,
  get,
  init,
  login,
  logout,
  logs,
  push,
  serve,
  train,
  version
]