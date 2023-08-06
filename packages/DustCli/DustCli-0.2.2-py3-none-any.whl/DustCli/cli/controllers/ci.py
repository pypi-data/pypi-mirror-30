"""DustCli ci controller."""

from cement.ext.ext_argparse import ArgparseController, expose
from pathlib import Path
from cement.utils import shell
import os
from DustCli.utils.git import GitUtil
import shutil
from shutil import ignore_patterns

ciPath = Path.home().joinpath('.dust', 'ci-scripts')


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
                (['-n', '--name'],
                 dict(action='store', help='脚本集的名称，例如：ci-script-for-destiny')
                 ),
                (['-g', '--git'],
                 dict(action='store', help='git 仓库的名称，例如: standard-swift-ci-scripts')
                 ),
            ])
    def init(self):
        git = self.app.pargs.git
        name = self.app.pargs.name
        if not name:
            self.app.log.error('请设置一个名字')
            return

        if not git and not self.app.args.unknown_args:
            self.app.log.error('请设置 git 地址')
            return

        target_path = ciPath.joinpath(name)
        if target_path.is_dir():
            shutil.rmtree(str(target_path))
        os.makedirs(str(target_path))

        self.app.args.unknown_args.append(git)
        repos = self.app.args.unknown_args
        file_from = {}
        for arg in repos:
            git_path = 'git@git.souche-inc.com:SCFEE/CI-Scripts/%s.git' % arg
            path = Path.home().joinpath('.dust', arg)
            GitUtil.clone(git_path, path)
            self.app.log.info('clone %s 完成' % arg)

            for file_name in os.listdir(str(path)):
                if file_name == '.git':
                    continue

                full_file_name = path.joinpath(file_name)
                file_target_path = target_path.joinpath(file_name)
                if file_target_path.exists():
                    self.app.log.info('文件 %s 重复：' % file_name)
                    options = [
                        '来自 %s ,已经存在' % file_from[file_name],
                        '来自 %s' % arg,
                    ]
                    source = shell.Prompt(
                        "选择使用哪个版本的文件：",
                        options=options,
                        numbered=True,
                    ).input
                    skip_copy = source in options
                    if skip_copy:
                        continue
                    else:
                        shutil.rmtree(str(file_target_path))

                shutil.copyfile(str(full_file_name), str(file_target_path))
                file_from[file_name] = arg

    @expose(help="运行 CI 命令",
            arguments=[
                (['-n', '--name'],
                 dict(action='store', help='脚本组的名字'),
                 ),
                (['-s', '--script'],
                 dict(action='store', help='脚本名称'),
                 ),
            ])
    def run(self):
        name = self.app.pargs.name
        script = self.app.pargs.script
        if not name:
            self.app.log.error('请设置脚本组的名字')
            return
        if not script:
            self.app.log.error('请设置要运行的脚本')
            return

        script_path = ciPath.joinpath(name, script + '.py')
        with open(str(script_path), 'r') as f:
            ci_code = f.read()

        exec(ci_code)

        if locals().get('dust_main', None) is None:
            self.app.log.error('脚本文件错误：请确保脚本文件中定义了 main 方法作为入口')
            return

        params = self.app.args.unknown_args
        locals()['dust_main'](*params)
