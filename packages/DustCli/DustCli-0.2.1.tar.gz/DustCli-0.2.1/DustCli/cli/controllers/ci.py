"""DustCli ci controller."""

from cement.ext.ext_argparse import ArgparseController, expose
from pathlib import Path
from DustCli.core.bundle import Bundle
from DustCli.core.merge import Merge
import os
from DustCli.utils.git import GitUtil

ciPath = Path.home().joinpath('.dust', 'CI')


class CIController(ArgparseController):
    class Meta:
        label = 'ci'
        description = '持续集成相关命令'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = []

    @expose(hide=True)
    def default(self):
        os.system('dust ci --help')

    @expose(help="初始化 CI 命令：从 gitlab 下载 python 脚本",
            arguments=[
                (['-g', '--git'],
                 dict(action='store', help='git 地址')
                 )
            ])
    def init(self):
        git = self.app.pargs.git
        if not git:
            self.app.log.error('请设置 git 地址')
            return

        GitUtil.clone(git, ciPath)
        self.app.log.info('clone %s 完成' % git)

    @expose(help="运行 CI 命令",
            arguments=[
                (['-n', '--name'],
                 dict(action='store', help='运行'),
                 ),
            ])
    def run(self):
        name = self.app.pargs.name
        if not name:
            self.app.log.error('请设置要运行的脚本')
            return

        script_path = ciPath.joinpath(name + '.py')
        with open(str(script_path), 'r') as f:
            ci_code = f.read()

        exec(ci_code)

        if locals().get('dust_main', None) is None:
            self.app.log.error('脚本文件错误：请确保脚本文件中定义了 main 方法作为入口')
            return

        params = self.app.args.unknown_args
        locals()['dust_main'](*params)
