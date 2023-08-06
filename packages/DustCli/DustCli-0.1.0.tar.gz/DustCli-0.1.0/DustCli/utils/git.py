import subprocess


class GitUtil(object):

    # 是否在git目录
    def is_git(self):
        return subprocess.getoutput('git status | grep "Not a git repository"') == ''

    # fetch
    def fetch(self):
        return subprocess.getoutput('git fetch')

    # 获取项目空间名
    def get_project_name(self):
        remote = subprocess.getoutput('git config --get remote.origin.url')
        
        if remote.find('.com/') >=0:
            project_name = remote.split('.com/')[1]
        elif remote.find('.com:') >=0:
            project_name = remote.split('.com:')[1]
        else:
            return ''

        return project_name.split('.git')[0].replace('/', '%2F')

    # 获取当前所在分支
    def get_current_branch(self):
        current_branch = subprocess.getoutput('git branch | grep "*"')
        if current_branch == '':
            return False
        return current_branch.split('* ')[1].split("\n")[0]

    # 获取 branch 上HEAD的commit id
    def get_head_commit(self, branch):
        return subprocess.getoutput('git rev-parse ' + branch)

    # branch是否存在 todo: 不严谨，待正则匹配
    def branch_is_exit(self, branch):
        return subprocess.getoutput('git branch -r | grep ' + branch) != ''


if __name__ == "__main__":
    git = Git()
    print('Test current branchName: ' + git.get_current_branch())
    print('Test get_head_commit: ' + git.get_head_commit('origin/test'))
