cd /tmp
/usr/bin/curl -s http://www.gromacs.org/@api/deki/files/40/=topolbuild1_2_1.tgz -o topolbuild1_2_1.tgz
/bin/tar xvfz topolbuild1_2_1.tgz
/bin/rm topolbuild1_2_1.tgz
/bin/cd topolbuild1_2_1/src
/usr/bin/make
sudo /bin/cp -r /tmp/topolbuild1_2_1 /opt
sudo /bin/chown qsar:qsar /opt/topolbuild1_2_1
