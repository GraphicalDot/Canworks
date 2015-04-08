#!/usr/bin/env python

from __future__ import with_statement
from fabric.api import show, local, settings, prefix, abort, run, cd, env, require, hide, execute
from fabric.contrib.console import confirm
from fabric.network import disconnect_all
from fabric.colors import green as _green, yellow as _yellow, red as _red
from fabric.contrib.files import exists
from fabric.utils import error
import os
import time

#env.use_ssh_config = True
#env.hosts = ["ec2-54-68-29-37.us-west-2.compute.amazonaws.com"] ##For t2 medium
#env.hosts = ["ec2-54-186-203-98.us-west-2.compute.amazonaws.com"] ##For m3.large
#env.user = "ubuntu"
#env.key_filename = "/home/k/Programs/Canworks/new_canworks.pem"
#env.warn_only = True

"""
This is the file which remotely makes an ec2 instance for the use of this repository
"""

HOME = os.path.expanduser("~")
VIRTUAL_ENVIRONMENT = "{0}/VirtualEnvironment".format(HOME)
PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def basic_setup():
	""""
	This method should be run before installing virtual environment as it will install python pip
	required to install virtual environment
	"""
	#run("sudo apt-get update")
	#run("sudo apt-get upgrade")
	run("sudo apt-get install -y python-pip")
	run("sudo apt-get install -y virtualenv")
	run("sudo apt-get install -y libevent-dev")
	run("sudo apt-get install -y python-all-dev")
	run("sudo apt-get install -y ipython")
	run("sudo apt-get install -y libxml2-dev")
	run("sudo apt-get install -y libxslt1-dev") 
	run("sudo apt-get install -y python-setuptools python-dev build-essential")
	run("sudo apt-get install -y libxml2-dev libxslt1-dev lib32z1-dev")
	run("sudo apt-get install -y python-lxml")
	#Dependencies for installating sklearn
	run("sudo apt-get install -y build-essential python-dev python-setuptools libatlas-dev libatlas3gf-base")
	#Dependencies for installating scipy
	run("sudo apt-get install -y liblapack-dev libatlas-dev gfortran")
	run("sudo apt-get install -y libatlas-base-dev gfortran build-essential g++ libblas-dev")
	#Dependicies to install hunpostagger
	run("sudo apt-get install -y ocaml-nox")
	run("sudo apt-get install -y mercurial")




def increase_swap():
	"""
	Scipy needs generally need more ram to install, this function increase the swap by allocating some harddisk 
	space to ram, which is slow but solves the purpose.
	Required only on amazom ec-2 micro instance
	"""

	run("sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024")
	run("sudo /sbin/mkswap /var/swap.1")
	run("sudo /sbin/swapon /var/swap.1")


def hunpos_tagger():
	"""
	This script installs the hunpos tagger 
	"""
	with cd("/home/ubuntu/VirtualEnvironment/canworks/trunk"):
		run("./build.sh build")
	
	with cd("/home/ubuntu/VirtualEnvironment/canworks"):
		run("sudo cp -r trunk/ /usr/local/bin")
		
	with cd("/usr/local/bin"):
		run("sudo wget https://hunpos.googlecode.com/files/en_wsj.model.gz")
		run("sudo gunzip en_wsj.model.gz")

def get_host():
        if env["host"] == "localhost":
                print "We are on localhost"
        else:
                print "We are on ec2"

def virtual_env():
	"""
	This method installs the virual environment and after installing virtual environment installs the git.
	After installing the git installs the reuiqred repository
	"""
	print '{0}/Canworks/'.format(PARENT_PATH) 
        if env["host"] == "localhost":
	        if not exists(VIRTUAL_ENVIRONMENT, use_sudo=True):
			run("virtualenv VirtualEnvironment")
                        with cd(VIRTUAL_ENVIRONMENT):
			        run("sudo cp -r {0} .".format(PATH))
                                with prefix("source bin/activate"):
			                if confirm("Do you want to install requirements.txt again??"):
		                                run("pip install -r Canworks/requirements.txt")
        else:
	        if not exists(VIRTUAL_ENVIRONMENT, use_sudo=True):
			run("virtualenv VirtualEnvironment")
                        with cd(VirtualEnvironment):
				        run("sudo apt-get install -y git")
				        with prefix("source bin/activate"):
					        if not exists("applogs", use_sudo=True):
						        run("sudo mkdir applogs")
						        run("sudo chown -R ubuntu:ubuntu applogs")
					        if not exists("Canworks", use_sudo=True):	
						        run(" git clone https://github.com/kaali-python/Canworks.git")
		        with prefix("source bin/activate"):
			        if confirm("Do you want to install requirements.txt again??"):
		                        run("pip install -r Canworks/requirements.txt")
                print "We are on some remote server"



def update_git_repo():
	with cd("/home/ubuntu/VirtualEnvironment"):
		with prefix("source bin/activate"):
			with cd("Canworks"):
				run(" git clone https://github.com/kaali-python/Canworks.git")


def install_text_sentence():
	"""
	If installs by pip shows an error"
	"""
	with cd("/home/ubuntu/VirtualEnvironment"):
		if not exists("text-sentence", use_sudo=True):	
			run ("sudo hg clone https://bitbucket.org/trebor74hr/text-sentence")
		with prefix("source bin/activate"):
			with cd("text-sentence"):
				run("/home/ubuntu/VirtualEnvironment/bin/python setup.py install")


def download_corpora():
	with cd(VirtualEnvironment):
		with prefix("source bin/activate"):
			print(_green("Now downloading textblob packages"))	
			run("python -m textblob.download_corpora")


	#nltk corpora
	with cd("/home/ubuntu/VirtualEnvironment/"):
		run("sudo python -m nltk.downloader all")

def mongo():
	"""
	This method installs the mongodb database on the remote server.It after installing the mongodb replaces the 
	mongodb configuration with the one available in the git repository.
	"""
	with prefix("cd /home/ubuntu/VirtualEnvironment"):
		run("sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10")
		run("echo -e 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list")
		run("sudo apt-get update")
		run("sudo apt-get install -y mongodb-10gen")
	run("sudo rm -rf  /var/lib/mongodb/mongod.lock")
	run("sudo service mongodb restart")


def disk_usage():
	    with settings(hide("running", "stderr", "stdout")):
	   	 result = run('df -h')
	    
	    print ("\n\n\t\t%s"%_yellow("Checking disk usage"))
	    print ("\n\n%s\n\n"%_green(result))

def ram_usage():
	    with settings(hide("running", "stderr", "stdout")):
	   	 result = run('free -m')
	    print ("\n\n\t\t%s"%_yellow("Checking ram usage"))
	    print ("\n\n%s\n\n"%_green(result))
	    return 


def supervisord_conf():
	with cd("/home/ubuntu/VirtualEnvironment/"):
		with prefix("source bin/activate"):
			run("sudo cp /home/ubuntu/VirtualEnvironment/Canworks/configs/supervisord.conf /etc/supervisord.conf")
			run("supervisorctl reload")	


def restart_with_new_repo():
	with cd("/home/ubuntu/VirtualEnvironment/"):
		with prefix("source bin/activate"):
			result = run('if ps aux | grep -v grep | grep -i "gunicorn"; then echo 1; else echo ""; fi')
	    		if result:
				print ("\n\n%s\n\n"%_green("Gunicorn is running"))
				confirmation = confirm("Do you want to restart gunicorn", default=True)
				if confirmation:
					pid = run("ps aux | grep gunicorn | awk 'NR==1 {print $2}'")
					run("sudo kill -9 %s"%pid)
		
	    				result = run('if ps aux | grep -v grep | grep -i "gunicorn"; then echo 1; else echo ""; fi')
					if not result:
						print ("\n\n%s\n\n"%_red("Gunicorn has been stopped and is starting with new repo"))
						with cd("Canworks"):
							run("git pull origin master")
							run("gunicorn -c configs/gunicorn_config.py api:app")
	    					result = run('if ps aux | grep -v grep | grep -i "gunicorn"; then echo 1; else echo ""; fi')
						if result:
							print ("\n\n%s\n\n"%_green("Gunicorn is running"))
							run("sudo service nginx restart")
						else:
							print ("\n\n%s\n\n"%_red("Gunicorn is not running, U need to login to the server"))
						

					else:
						print ("\n\n%s\n\n"%_red("Gunicorn has not been stopped"))
						return
			else:
				print ("\n\n%s\n\n"%_red("Gunicorn has been started yet"))
				with cd("Canworks"):
					run("gunicorn -c configs/gunicorn_config.py api:app")
					restart_with_new_repo()

def reboot():
	run("sudo reboot")


def health_check():
	print(_green("Connecting to EC2 Instance..."))	
	execute(mongo_status)
	execute(nginx_status)
	execute(gunicorn_status)
	execute(disk_usage)
	execute(ram_usage)
	print(_yellow("...Disconnecting EC2 instance..."))
	disconnect_all()



def update():
	print(_green("Connecting to EC2 Instance..."))	
	execute(update_git)
	execute(update_nginx_conf)
	execute(nginx_status)
		
	print(_yellow("...Disconnecting EC2 instance..."))
	disconnect_all()




def deploy():
	#print(_green("Connecting to EC2 Instance..."))	
	
	execute(basic_setup)
	#execute(virtual_env)
	#execute(update_git)
	#execute(install_text_sentence)
	#execute(download_corpora)
	#execute(nginx)
	#execute(mongo)
	#execute(restart_with_new_repo)
	#execute(health_check)
	#print(_yellow("...Disconnecting EC2 instance..."))
#	run("sudo reboot")
	#disconnect_all()



