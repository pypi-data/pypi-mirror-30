from cement.utils import shell
from pathlib import Path
import datetime


class Updater:

    @staticmethod
    def check_and_update(force=False):
        path = Path.home().joinpath('.dust', '.version-check')
        if not path.exists():
            shell.exec_cmd2(['touch', str(path)])

        with open(str(path)) as f:
            lines = f.readlines()
            if len(lines) <= 0:
                lines.append('0')

        time = float(lines[0])
        now = datetime.datetime.now().timestamp()

        if not force and now - time <= 86400:
            return

        print('正在检查版本...')
        stdout, stderr, exitcode = shell.exec_cmd(['pip3', 'search', 'DustCli', '--no-cache-dir'])
        if exitcode == 0:
            if 'LATEST:' in str(stdout):
                print('发现新版本，正在更新:')
                shell.exec_cmd2(['pip3', 'install', '--upgrade', 'DustCli'])
            else:
                print('正在使用最新版本，请放心使用')
        else:
            print("查询版本号失败: %s" % stderr)

        with open(str(path), 'w') as f:
            f.write(str(now))
