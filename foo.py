#!/usr/bin/env python3.6

from argparse import ArgumentParser
import configparser
from configparser import ConfigParser
import os
import shutil
import subprocess
import io
import shlex
### external libraries:
import git

# ==============================================================

def build_argparser() -> ArgumentParser:
    parser = ArgumentParser(
            prog='ebuild-repo-snapshot-ci.py',
            description='Ebuild Repository Snapshot CI'
        )
    parser.add_argument('--config',
            action='store',
            nargs=1,
            type=str,
            required=True,
            help='path to the config file',
            metavar='CONFIG',
            dest='config'
        )
    parser.add_argument('--output-dir',
            action='store',
            nargs=1,
            type=str,
            required=True,
            help='directory to which all data go',
            metavar='DIR',
            dest='out_dir'
        )

    return parser

def parse_cfg_file(cfg_file: str) -> ConfigParser:
    parser = ConfigParser(
            delimiters=('='),
            strict=True,
            comment_prefixes=('#', ';'),
            inline_comment_prefixes=('#'),
            empty_lines_in_values=False,
            interpolation=configparser.ExtendedInterpolation()
        )
    parser.read(cfg_file)

    return parser

# =======================================================

class repo:
    def __init__(self, config: ConfigParser, repo_name: str):
        raise NotImplementedError()

class git_repo(repo):

    name='' # type: str
    url='' # type: str
    branch = 'master' # type: str
    location = '' # type: str

    def __init__(self, cfg: ConfigParser, repo_name: str):
        self.name = repo_name
        self.url = cfg.get(repo_name, 'url')
        if cfg.has_option(repo_name, 'branch'):
            self.branch = cfg.get(repo_name, 'branch')

    def fetch(self, out_dir: str):
        self.location = out_dir

        ## here the magic happens
        repo = git.Repo.clone_from(self.url, out_dir,
                depth=1,
                single_branch=True,
                branch=self.branch
            )

        ## generate and save repo config
        repo_cfg = ConfigParser()
        repo_cfg['DEFAULT'] = {
                'url': self.url,
                'commit': repo.commit(),
                'timestamp': repo.commit().committed_date
            }
        repo_cfg_path = os.path.join(out_dir, 'repo.cfg')
        with open(repo_cfg_path, 'w') as configfile:
            repo_cfg.write(configfile)

        ## cleanup
        shutil.rmtree(repo.git_dir)
        repo.close()

def parse_repos(cfg):
    repos = cfg.get('DEFAULT', 'repositories') # type: str
    repos = repos.split(',')            # type: list
    repos = list(map(str.strip, repos)) # type: list

    obj_list = []
    for repo_name in repos:
        if not cfg.has_section(repo_name):
            raise Exception("Repository '{}' specified in repo_namesitories list, but no such section was found".format(repo_name))
        repo_type = cfg.get(repo_name, 'type')
        if repo_type == 'git':
            obj_list += [ git_repo(cfg, repo_name) ]
        else:
            raise Exception("Unknown repo_name type '{}' for repo_namesitory '{}'".format(repo_type, repo_name))

    return obj_list

def gen_md5_cache(repo_name):
    command = []
    if 'TRAVIS' in os.environ:
        command += ['travis_wait', str(CMD_TIMEOUT)]
    command += ['egencache', '--update', '--update-use-local-desc', '--update-pkg-desc-index', '--write-timestamp',
            '--config-root', '/tmp',
            '--jobs', str(MAX_JOBS),
            '--repo', repo_name,
            '--repositories-configuration', REPOS_CONF_STR,
        ]
    # since we're using shell, the cmd must be passed as a single argument
    cmd_str = " ".join(shlex.quote(x) for x in command)
    proc = subprocess.Popen(cmd_str,
        shell=True,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
    )

    # TODO: output something every minute

    proc.wait(CMD_TIMEOUT*60)

    if proc.returncode:
        print(proc.stdout.read().decode('utf-8'))
        print(" ".join(shlex.quote(a) for a in proc.args))
        raise Exception()

def generate_repos_conf(repos: list) -> str:
    repos_conf_cfg = ConfigParser()
    for repo in repos:
        repos_conf_cfg[repo.name]={
            'location': os.path.join(OUT_DIR_PATH, repo.name)
        }
    out = ''
    with io.StringIO() as foo:
        repos_conf_cfg.write(foo)
        out = foo.getvalue()

    return out

# ========================================================================================

argparser = build_argparser()

args = argparser.parse_args()
CFG_FILE_PATH = args.config[0]
OUT_DIR_PATH = args.out_dir[0]
MAX_JOBS = os.environ['MAX_JOBS'] if 'MAX_JOBS' in os.environ else 8
CMD_TIMEOUT = os.environ['CMD_TIMEOUT'] if 'CMD_TIMEOUT' in os.environ else 20

if not os.path.isfile(CFG_FILE_PATH):
    raise Exception("Config file '{0}' doesn't exist or is not accessible".format(CFG_FILE_PATH))
if not os.access(CFG_FILE_PATH, os.R_OK):
    raise Exception("Config file '{0}' is not readable".format(CFG_FILE_PATH))

parsed_cfg_file = parse_cfg_file(CFG_FILE_PATH)
repos = parse_repos(parsed_cfg_file)

## make sure output directory is OK
if os.path.exists(OUT_DIR_PATH):
    if not os.path.isdir(OUT_DIR_PATH):
        raise Exception("Output dir '{}' is not a directory".format(OUT_DIR_PATH))
else:
    os.mkdir(OUT_DIR_PATH)

REPOS_CONF_STR = generate_repos_conf(repos)

for repo in repos:
    repo_path = os.path.join(OUT_DIR_PATH, repo.name)
    repo.fetch(repo_path)

for repo in repos:
    gen_md5_cache(repo.name)
