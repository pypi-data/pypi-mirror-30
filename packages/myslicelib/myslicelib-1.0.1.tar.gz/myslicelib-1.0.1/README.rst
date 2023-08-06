MySliceLib Python module
=======================

MySliceLib python module, for more information: `<https://myslice.info>`

This module is a Library that alows to send Queries to SFA Registry and AMs

Install
=======================

::

    sudo apt-get -y install wget libssl-dev libcurl4-openssl-dev curl git
    sudo apt-get -y install python3-pip

    sudo apt-get update \
        && sudo apt-get -y upgrade \
        && sudo apt-get -y install software-properties-common python-software-properties \
		&& sudo add-apt-repository -y ppa:fkrull/deadsnakes \
        && sudo apt-get update \
        && sudo apt-get -y install python3.5 python3.5-dev \
        && sudo apt-get -y install libxml2-dev libxslt1-dev \
        && sudo curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" \
        && sudo python3.5 get-pip.py
    git clone git@gitlab.noc.onelab.eu:onelab/myslicelib.git
    cd myslicelib
    sudo pip3 install -r requirements.txt
    sudo python3.5 setup.py develop

Configure
=======================

You need a valid Private Key and Certificate matching a user account in SFA Registry

::

    /var/myslice/myslice.pkey
    /var/myslice/myslice.cert

