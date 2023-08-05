FROM fedora:27
RUN dnf install -y gcc gcc-c++ graphviz-devel ImageMagick python-devel libffi-devel openssl openssl-devel unzip nano autoconf automake libtool git python redhat-rpm-config; yum clean all
RUN curl https://bootstrap.pypa.io/get-pip.py | python -
RUN curl --silent --location https://rpm.nodesource.com/setup_8.x | bash -
RUN dnf install -y nodejs
RUN npm install -g bower;  echo '{ "allow_root": true }' > /root/.bowerrc

ADD . /code
WORKDIR /code

#installing optionally with celery since that
#may be a common usecase even though it's not an 
#absolute requirement (so not in setup.py)

RUN dnf install -y jq
RUN cd yadagehttpctrl && bower install
RUN pip install yadage[celery] redis
RUN pip install -e .
