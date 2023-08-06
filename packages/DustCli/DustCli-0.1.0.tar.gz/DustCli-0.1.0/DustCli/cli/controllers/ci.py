"""DustCli ci controller."""

from cement.ext.ext_argparse import ArgparseController, expose
from pathlib import Path
from DustCli.core.bundle import Bundle
from DustCli.core.merge import Merge
import os


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

    @expose(help="运行 CI 命令",
            arguments=[
                (['-c', '--custom'],
                 dict(action='store', help='自定义的命令'),
                 ),
                (['-i', '--init'],
                 dict(action='store_true', help='初始化'),
                 ),
                (['-mr', '--merge_request'],
                 dict(action='store_true', help='创建一个 mr')
                 )
            ])
    def run(self):
        ci_path = Path(os.getcwd()).joinpath('SCFEE.py')
        if not ci_path.exists():
            self.app.log.error('当前目录下没有发现 CI 配置文件，请进入对应目录再使用本命令')
            return

        with open(str(ci_path), 'r') as f:
            ci_code = f.read()

        exec(ci_code)

        if locals().get('init', None) is None or locals().get('merge_request', None) is None:
            self.app.log.error('配置文件错误：请确保配置文件中定义了 init 和 merge_request 方法')
            return

        if self.app.pargs.init:
            bundle = Bundle()
            locals()['init'](bundle)
            bundle.run()
        elif self.app.pargs.merge_request:
            merge = Merge()
            locals()['merge_request'](merge)

            merge.run()
        elif self.app.pargs.custom:
            func_name = self.app.pargs.custom
            locals()[func_name]()
        else:
            os.system('dust ci run --help')

