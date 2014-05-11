# QSAR

## Requirements

* [Git](http://git-scm.com/) >= ?
* [Python](https://www.python.org/) >= 3
* [Pip](http://www.pip-installer.org/en/latest/) >= ?
* [Virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) >= ?
* [PostgreSQL](http://www.postgresql.org/) >= 9.3
* [RabbitMQ](https://www.rabbitmq.com/) >= 3.3.1

To install these softwares follow their documentation.


## Installing and running <our-project-name>

### Clonning

Clone the <our-project-name> git repository and enter the project folder:

`$ git clone https://bitbucket.org/mdequeiroz/qsar && cd qsar`

### Preparing the environment

- Use [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) to create a virtual environment for python:

	`$ mkvirtualenv qsar -p path_to_python3`

- And then access the virtualenv you just created: `$ workon qsar`

- Go to `src/` folder and install the project requirements:

	`$ pip install -r requirements.txt`
	
---
For the next steps, you must be at `src/` folder.

### Preparing the database

`$ python manage.py syncdb`

### Running Django

`$ python manage.py runserver`

### Preparing Celery
Open a new terminal, access the virtualenv that was created with `$ workon qsar` and go to `src/` folder.

#### Running RabbitMQ

`$ sudo rabbitmq-server -detached`

#### Running worker

`$ celery qsar worker -l info`


Now, go to your favorite browser, type `http://127.0.0.1:8000/celery-test` and see the celery working.