# website

http://diamond-patterns.readthedocs.io/en/latest/patterns/website.html

To run the local server:

    make serve

The test website is available at [http://127.0.0.1:4000](http://127.0.0.1:4000).

## Setup

1. Configure web host
2. Create project for website
3. Configure git

### Configure web host

Create an Ansible role for the web host to contain this website.

    project-workon mccaul
    make www
    vi playbook.yaml

### Create project for website

Create a project for the website

    project-new3 www-project
    pip install diamond-patterns
    diamond --skel website scaffold
    git add -A
    git commit -am "initial commit"

### Configure git

Now unpack this project to create a git repository on the remote host.

    make git-init

If this site should automatically rebuild when a git push is received:

    make git-hooks

Re-add the original URL for origin so it backs up to the project repo:

    git remote -v
    git remote set-url origin --push --add Login@First-Repo.git
    git remote set-url origin --push --add Login@Second-Repo.git
    git remote -v

Now push the changes to rebuild the website.

    git push --set-upstream origin master
    git push -u origin --all
    git push -u origin --tags
