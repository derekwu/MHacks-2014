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
    env.key_filename = '~/.ssh/mealJetAdmin.pem'


def init_directories(virtenv_name, stage):
    
    with cd('~/'):
        run ('mkdir web')
        run ('mkdir web/%s.mealjet.co' % stage)

        run ('mkdir web/%s.mealjet.co/website' % stage)

        run ('mkdir web/%s.mealjet.co/logs' % stage)

        #Make two log files for supervisor process
        run('touch web/%s.mealjet.co/logs/access.log' % stage)
        run('touch web/%s.mealjet.co/logs/error.log' % stage)


def load_dependencies(virtenv_name, stage):

    sudo ('apt-get update')
    sudo ('apt-get install python python-pip git vim')
    sudo ('pip install virtualenv')

    with cd('web/%s.mealjet.co' % stage):
        run('virtualenv %s' % virtenv_name)


def init_git(virtenv_name, stage):

    with cd('~/web/%s.mealjet.co/website' % stage):
        run ('git init')
        git_ssh_path = prompt("What's the git SSH path: ")
        run ('git remote add origin %s' % git_ssh_path)
        run ('git pull origin %s' % stage)


def init(virtenv_name, stage):

    init_directories(virtenv_name, stage) 
    load_dependencies(virtenv_name, stage) 
    init_git(virtenv_name, stage)
    install_supervisor(virtenv_name, stage)


def beta(arg) :

    """This pushes to the EC2 instance defined below"""
    # The Elastic IP to your server
    env.host_string = '54.68.9.120'
    # your user on that system
    env.user = 'ubuntu' 
    # Assumes that your *.pem key is in the same directory as your fabfile.py
    env.key_filename = '~/.ssh/mealJetBeta.pem'

    stage = 'beta'

    # ex: 'prodenv' or 'betaenv'
    virtenv_name = stage + 'env'

    if(arg == 'init'):
        init(virtenv_name, stage)

    deploy(virtenv_name, stage)


def deploy(virtenv_name, stage) :


    # path to the directory on the server where your vhost is set up
    path = '/home/ubuntu/web/%s.mealjet.co' % stage
    
    # name of the application process

    print(red("Beginning Deploy:"))
    with cd("%s/website" % path) :
        run("pwd")
        print(green("Pulling master from GitHub..."))
        run("git pull origin %s" % stage)

        print(green("Installing requirements..."))
        run("source %s/%s/bin/activate && pip install -r reqs/%s.txt" % path, virtenv_name, stage)

        print(green("Collecting static files..."))
        #run("source %s/%s/bin/activate && python manage.py collectstatic --noinput" % path, virtenv_name, )


        print(green("Syncing the database..."))
        run("source %s/%s/bin/activate && python manage.py syncdb" % path, virtenv_name)

        print(green("Migrating the database..."))
        run("source %s/%s/bin/activate && python manage.py migrate" % path, virtenv_name)

        restart_gunicorn(virtenv_name)

    print(red("DONE!"))

def install_supervisor(virtenv_name, stage):

    # -f installs all the dependencies
    sudo('apt-get -f install supervisor')

    supervisor_file_path = '/etc/supervisor/conf.d/%s.conf' % virtenv_name

    # Remove old file if it exits
    sudo('rm -rf ' + supervisor_file_path)

    #Create a new empty file
    sudo('touch ' + supervisor_file_path)

    #Build new supervisor file
    sudo("echo '[program:%s]' >> %s" % (virtenv_name, supervisor_file_path))
    sudo("echo 'command = /home/ubuntu/web/%s.mealjet.co/app/bin/gunicorn_start' >> %s" % (stage, supervisor_file_path))
    sudo("echo 'user = ubuntu' >> %s" % supervisor_file_path)
    sudo("echo 'stdout_logfile =  /home/ubuntu/web/%s.mealjet.co/logs/access.log' >> %s" % (stage, supervisor_file_path))
    sudo("echo 'stderr_logfile =  /home/ubuntu/web/%s.mealjet.co/logs/error.log' >> %s" % (stage, supervisor_file_path))

    print(red("Done creating supervisor configs!"))

    #Make supervisor load new process from files
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

    print(red("Done installing supervisor!"))


def set_env_defaults():
    env.setdefault('remote_workdir', '/home/ubuntu/web/prod.mealjet.co/app')
    env.setdefault('gunicorn_pidpath', env.remote_workdir + '/run/gunicorn.pid')
    env.setdefault('virtualenv_dir', '/home/ubuntu/web/prod.mealjet.co/prodenv')
    env.setdefault('gunicorn_wsgi_app', '/home/ubuntu/web/prod.mealjet.co/app/gunicorn.py.ini')



def restart_gunicorn(virtenv_name):

    """Restart hard the Gunicorn process"""
    puts(colors.red("Stopping!"))
    sudo ('supervisorctl stop %s' % virtenv_name)
    puts(colors.red("Start!"))

    sudo ('supervisorctl start %s' % virtenv_name)


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
            run('%s /home/ubuntu/web/prod.mealjet.co/app/gunicorn.sh' % (prefix_string))
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