# QSAR

## Requirements

* [Git](http://git-scm.com/) >= ?
* [Python](https://www.python.org/) >= 3
* [Pip](http://www.pip-installer.org/en/latest/) >= ?
* [Virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) >= ?


## Installing and running

### Clonning

Clone the QSAR git repository and enter the project folder:
	
`$ git clone https://bitbucket.org/mdequeiroz/qsar && cd qsar`

### Preparing the environment

- Use [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) to create a virtual environment for python:

	`$ mkvirtualenv qsar -p path_to_python3`

- And then access the virtualenv you just created: `$ workon qsar`

- Go to `src/` folder and install the project requirements:

	`$ pip install -r requirements.txt`

### Running

`python run.py`

Now, go to your favorite browser, type `http://127.0.0.1:5000` and say hello!