from fabric.api import *
from fabric.api import settings
from fabric.colors import green, red
from fabric import colors
from time import sleep


def build_commit(warn_only=True):
    """Build a commit"""
    dev_branch = "dev"
    master_branch = "master"

    local('git checkout %s' % dev_branch)
    local('git add .')
    local('git add -u .')

    message  = prompt("commit message: ")

    local('git commit -m "%s"' % message)
    local('git checkout %s' % master_branch)
    local('git pull origin %s' % master_branch)
    local('git rebase %s' % dev_branch)
    local('git push origin %s' % master_branch)
    local('git checkout %s' % dev_branch)
    local('git push origin %s' % dev_branch)



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
        run("source %s/prodenv/bin/activate && pip install -r reqs/dev.txt" % path)
        print(green("Collecting static files..."))
        #run("source %s/prodenv/bin/activate && python manage.py collectstatic --noinput" % path)
        print(green("Syncing the database..."))
        run("source %s/prodenv/bin/activate && python manage.py syncdb" % path)
        print(green("Migrating the database..."))
        run("source %s/prodenv/bin/activate && python manage.py migrate" % path)
        restart_gunicorn()
    print(red("DONE!"))

def set_env_defaults():
    env.setdefault('remote_workdir', '/home/ubuntu/web/prod.mealjet.co/app')
    env.setdefault('gunicorn_pidpath', env.remote_workdir + '/run/gunicorn.pid')
    env.setdefault('virtualenv_dir', '/home/ubuntu/web/prod.mealjet.co/prodenv')
    env.setdefault('gunicorn_wsgi_app', '/home/ubuntu/web/prod.mealjet.co/app/gunicorn.py.ini')



def restart_gunicorn():
    """Restart hard the Gunicorn process"""
    stop()
    start()


def start():
    """Start the Gunicorn process"""

    if gunicorn_running():
        puts(colors.red("Gunicorn is already running!"))
        return

    if 'gunicorn_wsgi_app' not in env:
        abort(colors.red('env.gunicorn_wsgi_app not defined'))

    with cd(env.remote_workdir):
        prefix = []
        if 'virtualenv_dir' in env:
            prefix.append('source %s/bin/activate' % env.virtualenv_dir)
        

        prefix_string = ' && '.join(prefix)
        if len(prefix_string) > 0:
            prefix_string += ' && '

        options = [
            '--daemon',
            '--pid %s' % env.gunicorn_pidpath,
        ]
        
        options_string = ' '.join(options)

        if 'paster_config_file' in env:
            run('%s gunicorn_paster %s %s' % (prefix_string, options_string,
                                   env.paster_config_file))
        else:
            with settings(warn_only=True):
                result = run('%s gunicorn -c %s wsgi:application' % (prefix_string,
                                   env.gunicorn_wsgi_app))
                print result;
        puts (colors.green ("HERE"))
        if gunicorn_running():
            puts(colors.green("Gunicorn started."))
        else:
            abort(colors.red("Gunicorn wasn't started!"))



def stop():
    """Stop the Gunicorn process"""

    set_env_defaults()

    if not gunicorn_running():
        puts(colors.red("Gunicorn isn't running!"))
        return

    run('kill `cat %s`' % (env.gunicorn_pidpath))

    for i in range(0, 5):
        puts('.', end='', show_prefix=i == 0)

        if gunicorn_running():
            sleep(1)
        else:
            puts('', show_prefix=False)
            puts(colors.green("Gunicorn was stopped."))
            break
    else:
        puts(colors.red("Gunicorn wasn't stopped!"))
        return


def gunicorn_running_workers():
    count = None
    with hide('running', 'stdout', 'stderr'):
        count = run('ps -e -o ppid | grep `cat %s` | wc -l' %
                    env.gunicorn_pidpath)
    return count

def gunicorn_running():
    puts (colors.green ("HERE2"))
    return run('ls ' + env.gunicorn_pidpath, quiet=True).succeeded