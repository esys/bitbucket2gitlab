# Bitbucket To Gitlab

Migrate all source codes from a Git Bitbucket repository to GitLab.

## How it works

The script will loop on all Bitbucket projets and push all children repositories of a given Bitbucket projet in a Gitlab group.
By default, the GitLab group name will be the Bitbucket projet key name. However, this behaviour can be overriden using using a configuration file.

## Expectations

This script expects the following :

- Bitbucket repositories are accessed using HTTPS
- Bitbucket credentials are exported as environment variables
- GitLab is accessed using SSH
- Python 3.x installed and a working Git installation (/usr/bin/git)

## Configuration

Export Bitbucket credentials as environment variable :

```bash
export BITBUCKET_LOGIN=...
export BITBUCKET_PASSWORD=...
```

## Optional configuration

If you want a custom mapping between Bitbucket projets and Gitlab group, you can set a configuration file :

- by default, the script is looking for a file named bitbucket2gitlab.csv in the script directory
- configuration file location can be overriden as the first argument during the script invocation, i.e. `migrate.py "/path/to/config.csv"`

Configuration file format is :

- csv coma-separated
- with no header

Example :

```csv
bb_project1, gitlab_grp1
bb_project2, gitlab_grp2
...
```

## Usage

```bash
python migrate.py [/path/to/config.csv]
```
