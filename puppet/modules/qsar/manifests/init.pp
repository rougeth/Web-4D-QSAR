class qsar {

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

	# links virtualenvwrapper to load automaticaly
	file { '/etc/bash_completion.d/virtualenvwrapper.sh':
	    ensure => link,
	    target => '/usr/local/bin/virtualenvwrapper.sh',
		require => Package['virtualenvwrapper'],
	}
}
