#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Post gen hook to ensure that the generated project
has only one package management, either pipenv or pip."""
from pathlib import Path
import getpass
import json
import os
import requests
import shutil
import subprocess
import sys
from colorama import Fore, Style

def horizontal_rule():
    print(f'{Style.BRIGHT}{Fore.BLUE}―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――{Style.RESET_ALL}')

def log_blank_bright(message):
  print(f'   {Style.BRIGHT}{message}{Style.RESET_ALL}')

def log_check(message):
  print(f' {Style.BRIGHT}{Fore.GREEN}\N{HEAVY CHECK MARK} {Style.RESET_ALL}{message}')

def log_error(message):
  print(f'❌ {Style.BRIGHT}{Fore.RED}{message}{Style.RESET_ALL}')

def log_info(message):
  print(f'👉 {Style.BRIGHT}{message}{Style.RESET_ALL}')

def log_launch(message):
  print(f'🚀 {Style.BRIGHT}{message}{Style.RESET_ALL}')

def log_link(prefix="",url=""):
  print(f'   🌎 {Style.BRIGHT}{Fore.WHITE}{prefix} {Fore.CYAN}{url}{Style.RESET_ALL}')

def run(command,universal_newlines=True):
    cp = subprocess.run(
        command,
        universal_newlines=universal_newlines,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if int(cp.returncode) > 0:
        log_error(f'ERROR({cp.returncode}): {cp.stderr}')
        sys.exit(cp.returncode)

    return(cp.stdout.strip())

def add_and_commit():
    run(["git", "add", "--all"])
    run(["git", "-c", "commit.gpgsign=false", "commit", "-m", f'"Initial commit. Generated by cookiecutter-flask"'])

def create_github_repo(token, repo_name, repo_description):
    api_endpoint = 'https://api.github.com/user/repos'

    data = {
      'name': repo_name,
      'description': repo_description
    }

    headers = {'Authorization': f'token {token}'}

    response = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
    return response

def init_local_git_repo(git_url):
    run(["git", "init"])
    run(["git", "remote", "add", "origin", git_url])

def push_branch_to_github(branch_name="master"):
    run(["git", "-c", "commit.gpgsign=false", "push", "--set-upstream", "origin", branch_name])

def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False

if __name__ == "__main__":
    github_username = "{{cookiecutter.github_username}}"
    log_info(json.dumps(cookiecutter, indent=4))
    repo_name = "{{cookiecutter.github_repo}}"
    project_short_description = "{{cookiecutter.project_short_description}}"

    repo_git_url = f'git@github.com:{github_username}/{repo_name}.git'
    repo_web_url = f'https://github.com/{github_username}/{repo_name}'

    token = getpass.getpass(prompt='❓ Github Personal Access Token: ')

    message = f'Are you sure you want to create a new repo named {repo_name}?'
    git_response = yes_or_no(f'❓ {Style.BRIGHT}{message}{Style.RESET_ALL}')
    if not git_response == True:
        log_error("Exiting per user request not to continue")
        sys.exit(30)

    log_launch(f'Create a New Repo Named {repo_name}')
    github_response = create_github_repo(
        token,
        f'{repo_name}',
        f'{project_short_description}'
    )
    log_check(f'Status Code: {github_response.status_code}')

    log_check(f'Initialize {repo_name} Repo at {repo_git_url}')
    init_local_git_repo(repo_git_url)

    log_check(f'Add and Commit Initial Commit for {repo_name}')
    add_and_commit()

    log_check(f'Push to Github')
    push_branch_to_github()

    log_check('Heroku container login')
    run(["heroku", "container:login"])

    log_launch('Heroku Create')
    create_output = run(["heroku", "create", "-t", "learnsecurely"])
    log_check(create_output)

    log_launch('Heroku Container Push')
    push_output = run(["heroku", "container:push", "web"])
    log_check(push_output)

    log_launch('Heroku Release')
    release_output = run(["heroku", "container:release", "web"])
    log_check('Heroku Container Released')
    heroku_info_output = run(["heroku", "info"])

    horizontal_rule()
    log_info(f'A new repo named {repo_name} has been created')
    log_blank_bright(f'Links:')
    log_link("Git URL:", repo_git_url)
    log_link("Web URL:", repo_web_url)

    horizontal_rule()
    log_info(heroku_info_output)
