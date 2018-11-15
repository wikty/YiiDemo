import os
import shutil
import subprocess

from utils import tpl

post_receive_hook = r"""#!/bin/sh
#
# This script can't stop the push process, but the client doesn't
# disconnect until it has completed, so be careful if you try to 
# do anything that may take a long time.
#

echo "Composer start runinng..."
cd ..
composer install
echo "Composer done!"
"""

apache_virtual_host = r"""

<VirtualHost *:80>
    DocumentRoot "{{doc_root}}"
    
    ServerName {{host}}
    ServerAlias {{alias}}

    # ErrorLog "/the/path/to/error.log"
    # CustomLog "/the/path/to/access.log" common

    <Directory "{{doc_root}}web">
        Require all granted
        RewriteEngine on
        # prevent httpd from serving dotfiles (.htaccess, .svn, .git, etc.)
        RedirectMatch 403 /\..*$
        # if a directory or a file exists, use it directly
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        # otherwise forward it to index.php
        RewriteRule . index.php
    </Directory>

</VirtualHost>

"""


def init_project_repo(project_repo):
    output = []
    # init repo
    result = subprocess.run(['git', 'init', project_repo],
        shell=True,
        capture_output=True)
    result.check_returncode()  # raise a CalledProcessError if return non-zero
    output.append(str(result.stdout))
    # add repo
    result = subprocess.run(['git', 'add', '.'],
        cwd=project_repo,
        shell=True,
        capture_output=True)
    result.check_returncode()  # raise a CalledProcessError if return non-zero
    output.append(str(result.stdout))
    # commit repo
    result = subprocess.run([
            'git', 'diff', '--quiet',
            '&&',
            'git', 'diff', '--staged', '--quiet',
            '||',
            'git', 'commit', '-am', 'init commit'
        ],
        cwd=project_repo,
        shell=True,
        capture_output=True)
    result.check_returncode()  # raise a CalledProcessError if return non-zero
    output.append(str(result.stdout))
    return '\n'.join(output)


def init_test_repo(test_repo):
    if os.path.exists(test_repo):
        raise Exception('Test repo exists, please remove it first: {}'.format(
            test_repo))
    output = []
    # init repo
    result = subprocess.run(['git', 'init', test_repo],
        shell=True,
        capture_output=True)
    result.check_returncode()  # raise a CalledProcessError if return non-zero
    output.append(str(result.stdout))
    # config repo
    result = subprocess.run([
        'git', 'config', '--local', 'receive.denyCurrentBranch', 'updateInstead'],
        cwd=test_repo,
        shell=True,
        capture_output=True)
    result.check_returncode()
    output.append(str(result.stdout))
    # set post-receive hook
    hook_file = os.path.join(test_repo, '.git/hooks/post-receive')
    with open(hook_file, 'w', encoding='utf8') as f:
        f.write(post_receive_hook)
    output.append('Change the hook: .git/hooks/post-receive')
    return '\n'.join(output)


def init_dev_repo(dev_repo, test_repo, project_repo):
    if os.path.exists(dev_repo):
        raise Exception('Dev repo exists, please remove it first: {}'.format(
            dev_repo))
    repo_name = os.path.basename(dev_repo)
    parent_dir = os.path.dirname(dev_repo)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    output = []
    # clone from project repo
    result = subprocess.run(['git', 'clone', project_repo, repo_name],
        cwd=parent_dir,
        shell=True,
        capture_output=True)
    result.check_returncode()
    output.append(str(result.stdout))
    # remove remote
    result = subprocess.run(['git', 'remote', 'remove', 'origin'],
        cwd=dev_repo,
        shell=True,
        capture_output=True)
    result.check_returncode()
    output.append(str(result.stdout))
    # add remote
    result = subprocess.run(['git', 'remote', 'add', 'local', test_repo],
        cwd=dev_repo,
        shell=True,
        capture_output=True)
    result.check_returncode()
    output.append(str(result.stdout))
    # remove project repo
    # shutil.rmtree(os.path.join(project_repo, '.git'))
    return '\n'.join(output)


def config_virtual_host(hostname, test_repo):
    if len(hostname.split(';')) == 2:
        host, alias = hostname.split(';')
    else:
        host, alias = hostname, '{}.com'.format(hostname)
    test_repo = test_repo.rstrip(os.path.sep) + os.path.sep
    return tpl(apache_virtual_host, 
        doc_root=test_repo,
        host=host,
        alias=alias)