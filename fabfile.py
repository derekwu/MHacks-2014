from fabric.api import *
from fabric.colors import green, red

def build_commit(warn_only=True):
    """Build a commit"""
    local_branch = prompt("checkout branch: ")
    rebase_branch = prompt("rebase branch: ")

    local('git checkout %s' % local_branch)
    local('git add .')
    local('git add -u .')

    message  = prompt("commit message: ")

    local('git commit -m "%s"' % message)
    local('git checkout %s' % rebase_branch)
    local('git pull origin %s' % rebase_branch)
    local('git checkout %s' % local_branch)
    local('git rebase %s' % rebase_branch)
    local('git checkout %s' % rebase_branch)
    local('git merge %s' % local_branch)
    local('git push origin %s' % rebase_branch)
    local('git checkout %s' % local_branch)


def server() :
    """This pushes to the EC2 instance defined below"""
    # The Elastic IP to your server
    env.host_string = '54.68.28.106'
    # your user on that system
    env.user = 'ubuntu' 
    # Assumes that your *.pem key is in the same directory as your fabfile.py
    env.key_filename = "~/.ssh/mealJetAdmin.pem"

def staging() :
    # path to the directory on the server where your vhost is set up
    path = "/home/ubuntu/web/prod.mealjet.co"
    # name of the application process

    print(red("Beginning Deploy:"))
    with cd("%s/app" % path) :
        run("pwd")
        print(green("Pulling master from GitHub..."))
        run("git pull origin master")
        print(green("Installing requirements..."))
        run("sudo source %s/prodenv/bin/activate && pip install -r requirements.txt" % path)
        print(green("Collecting static files..."))
        run("sudo source %s/prodenv/bin/activate && python manage.py collectstatic --noinput" % path)
        print(green("Syncing the database..."))
        run("sudo source %s/prodenv/bin/activate && python manage.py syncdb" % path)
        print(green("Migrating the database..."))
        run("sudo source %s/prodenv/bin/activate && python manage.py migrate" % path)
        print(green("closing the gunicorn process"))
        run("kill `cat run/gunicorn.pid`")
        print(green("Starting the gunicorn process"))
        run("gunicorn -c gunicorn.py.ini wsgi:application")
    print(red("DONE!"))
