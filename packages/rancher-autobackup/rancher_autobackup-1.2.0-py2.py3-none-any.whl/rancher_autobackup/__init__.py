from pathlib import Path

import os
import requests
import subprocess
import sys


VERSION = '1.2.0'


def stderrprint(*printargs, **kwargs):
    print(*printargs, file=sys.stderr, **kwargs)


class Git:
    def __init__(self, gitdir, git_user_name, git_user_email, ssh_private_key_file):
        self.gitdir = gitdir
        self.git_user_name = git_user_name
        self.git_user_email = git_user_email
        self.git_env = os.environ.copy()
        self.git_env["GIT_SSH_COMMAND"] = "ssh -o StrictHostKeyChecking=no -o IdentityFile=" + ssh_private_key_file

    def config(self):
        self.execute('-C', self.gitdir, 'config', 'user.name', self.git_user_name)
        self.execute('-C', self.gitdir, 'config', 'user.email', self.git_user_email)

    def execute(self, *gitargs):
        return subprocess.run(['git'] + list(gitargs), env=self.git_env, check=False)

    def add_commit_and_push(self, git_commit_message, git_branch):
        if self.execute('-C', self.gitdir, 'add', '.').returncode > 0:
            raise Exception('Git add error')
        if self.execute('-C', self.gitdir, 'commit', '-m', '"' + git_commit_message + '"').returncode > 1:
            raise Exception('Git commit error')
        if self.execute('-C', self.gitdir, 'push', 'origin', git_branch).returncode > 1:
            raise Exception('Git push error')


class Api:
    def __init__(self, rancher_url, credentials, environment_id, tmpdir):
        self.rancher_url = rancher_url
        self.credentials = credentials
        self.tmpdir = tmpdir
        if environment_id is None:
            self.environment_id = self.get_environment_id()
        else:
            self.environment_id = environment_id

    def get_environment_id(self):
        with requests.get(url=self.rancher_url + '/v2-beta/projects/', auth=self.credentials) as result:
            data = result.json()
            return data['data'][0]['id']

    def get_compose_data_and_write_to_files(self):
        json_header = {'Content-Type': 'application/json'}
        payload = {"serviceIds": []}

        with requests.get(url=self.rancher_url + '/v2-beta/projects/' + self.environment_id + '/stacks?system=false',
                          auth=self.credentials) as result:
            data = result.json()
            for stack in [x for x in data["data"] if x["type"] == "stack"]:
                print(stack["name"])
                actions = stack["actions"]
                exportconfig_url = actions["exportconfig"]
                with requests.post(url=exportconfig_url, auth=self.credentials, headers=json_header,
                                   json=payload) as exportconfig_result:
                    exportconfig_data = exportconfig_result.json()
                    Path(self.tmpdir + '/' + stack["name"]).mkdir(exist_ok=True)
                    with open(self.tmpdir + '/' + stack["name"] + '/docker-compose.yml', 'w') as file:
                        file.write(exportconfig_data["dockerComposeConfig"])
                    with open(self.tmpdir + '/' + stack["name"] + '/rancher-compose.yml', 'w') as file:
                        file.write(exportconfig_data["rancherComposeConfig"])

