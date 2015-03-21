# Web 4D-QSAR
Open source web system to generate and validate QSAR modules.



## Requirements

The **Web 4D-QSAR** was built and tested using Ubuntu 14.04 LTS but it should run without problems in any Linux distribution that supports the following softwares:

* [Git](http://git-scm.com/) >= ?
* [Python](https://www.python.org/) >= 3
* [Pip](http://www.pip-installer.org/en/latest/)
* [Virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) >= ?
* [PostgreSQL](http://www.postgresql.org/) >= 9.3
* [RabbitMQ](https://www.rabbitmq.com/) >= 3.3.1
* [Gromacs](https://gromacs.org) >= 4.6.5
* [LQTAGridPy](https://github.com/rougeth/LQTAgridPy)
* [dos2unix](http://dos2unix.sourceforge.net)


## Preparing the machine (Ubuntu 14.04 LTS)

> **\* It should be automated using Puppet**


### Development requirements

* build-essential/cmake
* git
* python/python-dev/python-pip
* rabbitmq-server

```
$ sudo apt-get install build-essential cmake git python python-dev python-pip rabbitmq-server
```

* virtualenvwrapper

```
$ pip install virtualenvwrapper

$ echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
$ echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc

or

$ export WORKON_HOME=$HOME/.virtualenvs
$ export PROJECT_HOME=$HOME/devel
$ export /usr/local/bin/virtualenvwrapper.sh

```

### Dynamic requirements

#### Gromacs

```
$ sudo apt-get install gromacs
```

#### Topolbuild

```
$ cd /tmp
$ wget -nv http://www.gromacs.org/@api/deki/files/40/=topolbuild1_2_1.tgz -O topolbuild1_2_1.tgz
$ tar xvfz topolbuild1_2_1.tgz
$ cd topolbuild1_2_1/src
$ make
$ sudo cp -r /tmp/topolbuild1_2_1 /opt
$ sudo chmod a+x /opt/topolbuild1_2_1/src/topolbuild
$ sudo ln -s /opt/topolbuild1_2_1/src/topolbuild /usr/bin/topolbuild
```

## Installing and running Web 4D-QSAR

### Clonning the repository

Clone the **Web 4D-QSAR** git repository and enter the project folder:

`$ git clone https://github.com/rougeth/web-4d-qsar && cd web-4d-qsar`

### Preparing the environment

- Use [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) to create a virtual environment for python:

	`$ mkvirtualenv web-4d-qsar -p path_to_python3`

	In Ubuntu 14.04, the path to python 3 is */usr/bin/python3*

- To access the virtualenv you just created: `$ workon qsar`
	Note that you will see the name of the environment in the PS1 variable: `(env_name) $`

- Install the required Python packages (you need to have the env activated):

	`$ pip install -r requirements.txt`

---

For the next steps, you must be at `src/` folder.

### Preparing the database

`$ python manage.py syncdb`

*No need of creating superuser.*


### Running Django

`$ python manage.py runserver`

### Preparing Celery

Open a new terminal, access the virtualenv that was created with `$ workon web-4d-qsar` and go to `src/` folder.

#### Running RabbitMQ

`$ sudo rabbitmq-server -detached`

#### Running worker

`$ celery -A web-4d-qsar worker -l info`

Now, go to your favorite browser, type `http://127.0.0.1:8000` and see the celery working.
