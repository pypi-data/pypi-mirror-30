"""DustCli bootstrapping."""

from DustCli.cli.controllers.base import BaseController
from DustCli.cli.controllers.project import ProjectController, SDKController
from DustCli.cli.controllers.package import PackageController
from DustCli.cli.controllers.ci import CIController
from DustCli.cli.controllers.mr import MRController


def load(app):
    app.handler.register(BaseController)
    app.handler.register(ProjectController)
    app.handler.register(SDKController)
    app.handler.register(PackageController)
    app.handler.register(CIController)
    app.handler.register(MRController)
