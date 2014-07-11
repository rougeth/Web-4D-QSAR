class web_4d_qsar {

    include web_4d_qsar::requirements
    #include supervisor

    group { 'qsar':
        ensure => present,
    }

	user { 'qsar':
		ensure     => 'present',
        managehome => true,
        shell      => '/bin/bash',
        gid        => 'qsar',
        groups     => ['sudo'],
	}

    # supervisor::app { 'celery':
    #     command   => '/home/vagrant/.virtualenvs/qsar/bin/celery -A qsar worker -l info',
    #     directory => '/qsar/src',
    #     user      => 'qsar',
    # }
}
