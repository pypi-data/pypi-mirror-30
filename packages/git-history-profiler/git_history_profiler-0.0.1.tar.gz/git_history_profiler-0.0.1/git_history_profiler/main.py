import os
import time
import shutil
from io import StringIO

from typing import Optional, List

import sh
import click

import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

from tqdm import tqdm

from .utils import load_config


class Repository:
    def __init__(self, url: str, config: str) -> None:
        self.url = url

        self.config_dir = os.path.dirname(config)
        self.config = load_config(config)
        os.makedirs(self.config['working_directory'])

    @property
    def repo_dir(self) -> str:
        return os.path.abspath(os.path.join(
            self.config['working_directory'], 'repo'))

    def clone(self) -> None:
        if os.path.exists(self.url):
            # is local
            shutil.copytree(self.url, self.repo_dir)
        else:
            # is remote
            sh.git.clone(
                self.url, 'repo',
                _cwd=self.config['working_directory'])

    def clean(self) -> None:
        sh.git.checkout('.', _cwd=self.repo_dir)

    def switch_to_commit(self, commit_id: str) -> None:
        # switch to commit
        sh.git.checkout(commit_id, _cwd=self.repo_dir)

        # prepare environment
        cmd_path = os.path.join(self.config_dir, self.config['init_script'])
        os.system(f'{cmd_path} "{self.repo_dir}" > /dev/null')

    def execute(self) -> List:
        stats = []
        for job in tqdm(self.config['jobs'], desc='Jobs'):
            cmd_path = os.path.join(self.config_dir, job['command'])
            # cmd = sh.Command(cmd_path)

            start = time.time()
            # cmd(_cwd=self.repo_dir)
            os.system(f'cd "{self.repo_dir}" && {cmd_path} > /dev/null')
            dur = time.time() - start

            stats.append((job['name'], dur))
        return stats

    def handle_commit(self, commit_id: str) -> List:
        self.clean()
        self.switch_to_commit(commit_id)
        return self.execute()

    def list_commits(self) -> List[str]:
        buf = StringIO()
        sh.git(
            'rev-list', '--all', '--reverse', _out=buf,
            _cwd=self.repo_dir)
        return buf.getvalue().split()

    def parse_commits(self, commits: Optional[List[str]]) -> List[str]:
        all_commits = self.list_commits()
        if commits is None:
            return all_commits

        new_commits = []
        for commit in commits:
            if '..' in commit:
                com1, com2 = commit.split('..')
                idx1, idx2 = all_commits.index(com1), all_commits.index(com2)
                new_commits.extend(all_commits[idx1:idx2+1])
            else:
                new_commits.append(commit)

        return new_commits

    def run(self, commits: Optional[List[str]] = None) -> List:
        self.clone()

        stats = []
        commits = self.parse_commits(commits)

        for commit in tqdm(commits, desc='Commit history'):
            res = self.handle_commit(commit)
            stats.append((commit, res))
        return stats

    def plot(self, data: List) -> None:
        # transform data
        tmp = []
        for commit, jobs in data:
            for name, duration in jobs:
                tmp.append((commit[:7], name, duration))
        df = pd.DataFrame(tmp, columns=['commit', 'job', 'time'])

        # plot
        sns.pointplot(x='commit', y='time', hue='job', data=df)

        plt.xticks(rotation=90)
        plt.xlabel('Commits [id]')
        plt.ylabel('Execution time [s]')
        plt.title('Performance overview')

        plt.tight_layout()
        plt.savefig(os.path.join(
            self.config['working_directory'], 'performance.pdf'))


@click.command()
@click.argument('repo_url')
@click.option(
    '--config', required=True,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help='Path to config.')
@click.option(
    '-c', '--commit', multiple=True,
    help='Commit id to consider.')
def main(repo_url: str, config: str, commit: List[str]) -> None:
    """ Performance and stability profiling over the git commit history.
    """
    repo = Repository(repo_url, config)

    res = repo.run(commit if len(commit) > 0 else None)
    repo.plot(res)


if __name__ == '__main__':
    main()
