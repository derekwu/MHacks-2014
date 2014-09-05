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
    env.host_string = '54.68.65.7'
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
    sudo ('apt-get install python  python-dev python-pip git mysql-server mysql-client libmysqlclient-dev nginx')
    sudo ('pip install virtualenv')

    with cd('web/%s.mealjet.co' % stage):
        run('virtualenv %s' % virtenv_name)


def init_git(virtenv_name, stage):

    #default_remote_file_name = 'git_ssh_file.pem' 
    #run('mkdir -p ~/.ssh && chmod 700 ~/.ssh')

    #with cd("~/.ssh"):
    #  git_ssh_key_file = prompt("What's the path to the git SSH key file?")
    #  
    #  #upload file, and set permissions
    #  run("touch %s" % default_remote_file_name)
    #  put(git_ssh_key_file, default_remote_file_name)
    #  run("chmod 600 %s" % default_remote_file_name)       
    #  
    #  #Add git to config file
    #  run("echo -e 'Host bitbucket.org' >> config")
    #  run("echo -e '\t IdentityFile ~/.ssh/%s' >> config" % default_remote_file_name)
    #  run("echo -e ' '") # Adding space so can append other Host's later 

    with cd('~/web/%s.mealjet.co/website' % stage):
        run ('git init')
        git_ssh_path = prompt("What's the git SSH path: ")
        run ('git remote add origin %s' % git_ssh_path)
        run ('git pull origin %s' % stage)

def init_database ():

    new_user = prompt ("Enter new user name: ")
    new_user_password = prompt ("Enter new user password: ")
    new_db_name = prompt ("Enter new database name: ")
    root_password = prompt ("Enter ROOT password: ")

    MYSQL_CREATE_USER = """CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';"""% (new_user,new_user_password)

    MYSQL_CREATE_DB = """CREATE DATABASE %s DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;""" % (new_db_name)

    MYSQL_GRANT_PERMISSIONS = """GRANT ALL ON %s.* TO '%s'@'localhost';FLUSH PRIVILEGES;""" % (new_db_name,new_user)

    run('echo "%s" | mysql --user="%s" --password="%s"' % (MYSQL_CREATE_USER, "root" , root_password))
    run('echo "%s" | mysql --user="%s" --password="%s"' % (MYSQL_CREATE_DB, "root" , root_password))
    run('echo "%s" | mysql --user="%s" --password="%s"' % (MYSQL_GRANT_PERMISSIONS, "root" , root_password))



def init(virtenv_name, stage):

    init_directories(virtenv_name, stage) 
    load_dependencies(virtenv_name, stage) 
    init_git(virtenv_name, stage)
    install_supervisor(virtenv_name, stage)
    init_nginx(virtenv_name, stage)


def beta(arg) :

    """This pushes to the EC2 instance defined below"""
    # The Elastic IP to your server
    env.host_string = '54.68.65.7'
    #env.host_string = '54.68.9.120'
    # your user on that system
    env.user = 'ubuntu' 
    # Assumes that your *.pem key is in the same directory as your fabfile.py
    env.key_filename = '~/.ssh/mealJetAdmin.pem'

    stage = 'beta'

    # ex: 'prodenv' or 'betaenv'
    virtenv_name = stage + 'env'

    if(arg == 'init'):
        init(virtenv_name, stage)
        init_database_flag = str(prompt ("Do you want to create a new database and user Y/n: "))
        if (init_database_flag == "y" or init_database_flag == "Y" or init_database_flag==""):
            init_database()

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

        #TODO CHANGE TO BETA!!!!!!!
        print(green("Installing requirements..."))
        run("source %s/%s/bin/activate && pip install -r reqs/dev.txt" % ( path, virtenv_name) )

        print(green("Collecting static files..."))
        #run("source %s/%s/bin/activate && python manage.py collectstatic --noinput" % ( path, virtenv_name ) )


        print(green("Syncing the database..."))
        run("source %s/%s/bin/activate && python manage.py syncdb" % ( path, virtenv_name ) )

        print(green("Migrating the database..."))
        run("source %s/%s/bin/activate && python manage.py migrate" % ( path, virtenv_name ) )

        restart_gunicorn(virtenv_name)

    print(red("DONE!"))

def init_nginx(virtenv_name, stage):

    kwargs = { 'stage' : stage }
    
    with cd('~/web/%s.mealjet.co/website' % stage): 
        nginx_conf = open('nginx.conf.template').format(**kwargs)
    
    sudo("echo '%s' > /etc/nginx/sites-available/mealjet")
    sudo("ln -s /etc/nginx/sites-available/mealjet /etc/nginx/sites-enabled/mealjet")

    sudo("nginx -t")
    sudo("service nginx restart")

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
    sudo("echo 'command = /home/ubuntu/web/%s.mealjet.co/website/bin/gunicorn_start --environment %s' >> %s" % (stage, stage, supervisor_file_path))
    sudo("echo 'user = ubuntu' >> %s" % supervisor_file_path)
    sudo("echo 'stdout_logfile =  /home/ubuntu/web/%s.mealjet.co/logs/access.log' >> %s" % (stage, supervisor_file_path))
    sudo("echo 'stderr_logfile =  /home/ubuntu/web/%s.mealjet.co/logs/error.log' >> %s" % (stage, supervisor_file_path))

    print(red("Done creating supervisor configs!"))

    #Make supervisor load new process from files
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

    print(red("Done installing supervisor!"))


def restart_gunicorn(virtenv_name):

    """Restart hard the Gunicorn process"""
    puts(colors.red("Stopping!"))
    sudo ('supervisorctl stop %s' % virtenv_name)
    puts(colors.red("Start!"))

    sudo ('supervisorctl start %s' % virtenv_name)

