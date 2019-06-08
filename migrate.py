import csv
import sys
import os
from subprocess import call
import requests
from requests.auth import HTTPBasicAuth

BITBUCKET_URL = 'https://bitbucket/rest/api/1.0'
GITLAB_URL = 'https://gitlab'
GIT_BIN = '/usr/bin/git'
WORK_DIR = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'work'


def validate_env():
    if os.environ['BITBUCKET_LOGIN'] is None or os.environ['BITBUCKET_PASSWORD'] is None:
        print('Missing environment variable BITBUCKET_LOGIN and/or BITBUCKET_PASSWORD')
        return False
    return True


def load_configuration():
    bitbucket2gitlab = dict()
    cfg_filename = 'bitbucket2gitlab.csv'
    if len(sys.argv) > 1:
        cfg_filename = sys.argv[1]
    with open(cfg_filename, 'r') as csvfile:
        parser = csv.reader(csvfile, delimiter=',')
        for row in parser:
            if len(row) < 2:
                print('ignoring: ' + row)
                continue
            bitbucket2gitlab[row[0].strip()] = row[1].strip()

    return bitbucket2gitlab


def get_bitbucket_projects(path, login, password):
    resp = requests.get('{}/{}'.format(BITBUCKET_URL, path),
                        auth=HTTPBasicAuth(login, password))
    if resp.status_code != 200:
        print('cannot connect to bitbucket when fetching', path)
        print(resp.text)
        exit(1)
    return resp


def main():
    if not validate_env():
        exit(1)

    bitbucket2gitlab = load_configuration()
    if not bitbucket2gitlab:
        print('Empty configuration, nothing to do')
        exit(0)

    with open('bitbucket2gitlab.csv', 'r') as csvfile:
        parser = csv.reader(csvfile, delimiter=',')
        for row in parser:
            if len(row) < 2:
                print('ignoring: ' + row)
                continue
            bitbucket2gitlab[row[0].strip()] = row[1].strip()

    bb_projects = dict()
    bb_login = os.environ['BITBUCKET_LOGIN']
    bb_password = os.environ['BITBUCKET_PASSWORD']
    # TODO: properly handle paging
    resp = get_bitbucket_projects(
        'projects?limit=100', bb_login, bb_password)

    for project in resp.json()['values']:
        bb_projects[project['key']] = project
        key = project['key']
        project_name = project['name']
        group = key
        if key not in bitbucket2gitlab:
            print(
                'No custom gitlab group found for bitbucket key', key, 'default to gitlab group', group)

        print('Migrating source for project', key, project_name)
        resp = get_bitbucket_projects(
            'projects/{}/repos?limit=200'.format(key), bb_login, bb_password)

        for repo in resp.json()['values']:
            repo_slug = repo['slug']
            resp = get_bitbucket_projects(
                'projects/{}/repos/{}'.format(key, repo_slug), bb_login, bb_password)
            clone_url = None
            for url in resp.json()['links']['clone']:
                if url['name'] == 'ssh':
                    clone_url = url['href']
            if clone_url is None:
                print('Http clone url not found for', repo_slug)
                continue
            print(clone_url)

            print('> From Bitbucket : cloning repository', repo_slug)
            clone_dir = "{}/{}".format(WORK_DIR, repo_slug)
            code = call([GIT_BIN, 'clone', '--bare', clone_url, clone_dir])
            if code != 0:
                print('Git clone failed for', repo_slug)
                continue

            print('> To GitLab : pushing new repository',
                  repo_slug, 'in group', group)
            gitlab_repo_url = '{}/{}/{}.git'.format(
                GITLAB_URL, group, repo_slug)
            code = call([GIT_BIN, 'push', '--mirror', gitlab_repo_url])
            if code != 0:
                print('Git push failed for', repo_slug)


if __name__ == "__main__":
    main()
