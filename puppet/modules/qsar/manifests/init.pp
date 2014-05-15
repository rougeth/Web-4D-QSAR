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
}
