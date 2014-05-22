class qsar {

	user { 'qsar':
		name => 'qsar',
		password => 'qsar',
		ensure => 'present',
		groups => 'root',
	}

	package { 'build-essential':
	    ensure => installed,
	}

	package { 'cmake':
		ensure => installed,
	}

	package { 'gromacs':
		ensure => installed,
	}

	package { 'git':
		ensure => installed,
	}

	package { 'python-pip':
		ensure => installed,
	}

	package { 'virtualenvwrapper':
		ensure => installed,
		provider => pip,
		require => Package['python-pip'],
	}

	# links virtualenvwrapper to load automatically
	file { '/etc/bash_completion.d/virtualenvwrapper.sh':
	    ensure => link,
	    target => '/usr/local/bin/virtualenvwrapper.sh',
		require => Package['virtualenvwrapper'],
	}

	package { 'rabbitmq-server':
		ensure => installed,
	}

	file { '/qsar/bin':
		ensure => "directory",
	}
}
