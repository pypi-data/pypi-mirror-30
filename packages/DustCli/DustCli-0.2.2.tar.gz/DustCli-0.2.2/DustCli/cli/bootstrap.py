"""DustCli bootstrapping."""

from DustCli.utils.updater import Updater

from cement.ext.ext_argparse import ArgparseArgumentHandler
from DustCli.cli.controllers.base import BaseController
from DustCli.cli.controllers.project import ProjectController, SDKController
from DustCli.cli.controllers.package import PackageController
from DustCli.cli.controllers.ci import CIController
from DustCli.cli.controllers.mr import MRController


class ModifiedArgparseArgumentHandler(ArgparseArgumentHandler):
    class Meta:
        label = 'dust_arg_parse'
        ignore_unknown_arguments = True


def load(app):
    Updater.check_and_update()
    app.handler.register(ModifiedArgparseArgumentHandler)
    app.handler.register(BaseController)
    app.handler.register(ProjectController)
    app.handler.register(SDKController)
    app.handler.register(PackageController)
    app.handler.register(CIController)
    app.handler.register(MRController)
