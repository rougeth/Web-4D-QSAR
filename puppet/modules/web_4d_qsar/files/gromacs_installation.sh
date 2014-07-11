mkdir /web-4d-qsar/bin
curl -s ftp://ftp.gromacs.org/pub/gromacs/gromacs-4.6.5.tar.gz -o ./gromacs-4.6.5.tar.gz
tar xfz gromacs-4.6.5.tar.gz
rm gromacs-4.6.5.tar.gz
mkdir gromacs-4.6.5/build
cd gromacs-4.6.5/build
cmake .. -DGMX_BUILD_OWN_FFTW=ON
make
make install
echo export PATH=/usr/local/gromacs/bin:$PATH >> ~/.bashrc
