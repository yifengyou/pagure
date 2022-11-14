FROM rockylinux:8.6
LABEL maintainers="yifengyou <nicyou@tencent.com>"

RUN dnf install -y epel-release && cat /etc/yum.repos.d/*.repo && dnf makecache && \
    dnf -y --enablerepo powertools install systemd findutils gcc git libgit2-devel python3-alembic \
                   python3-arrow python3-bcrypt python3-beautifulsoup4 \
                   python3-binaryornot python3-bleach \
                   python3-blinker python3-celery python3-chardet \
                   python3-coverage python3-cryptography python3-devel \
                   python3-docutils python3-eventlet  \
                   python3-fedora python3-fedora-flask python3-filelock \
                   python3-flake8 python3-flask python3-flask-oidc \
                   python3-flask-wtf python3-jinja2 \
                   python3-kitchen python3-markdown python3-mock \
                   python3-munch \
                   python3-openid python3-openid-cla python3-openid-teams \
                   python3-pillow python3-psutil python3-psycopg2 \
                   python3-pygit2 python3-redis python3-requests \
                   python3-setuptools python3-six python3-sqlalchemy \
                   python3-straight-plugin python3-trololio \
                   python3-wtforms which passwd \
                   python3-email-validator \
                   python3-mysql \
                   python3-whitenoise openssh-server mysql-server \
                   && \
    dnf install -y pagure pagure-milters \
    pagure-mirror \
    pagure-ev pagure-webhook \
    nginx pagure-web-nginx redis net-tools python3-gunicorn procps-ng \
    sqlite vim && \
    dnf clean all
COPY files/systemd/*.timer /usr/lib/systemd/system/
COPY files/systemd/*.service /usr/lib/systemd/system/
COPY files/pagure.conf /etc/nginx/conf.d/pagure.conf
COPY files/pagure.cfg /etc/pagure/pagure.cfg
COPY files/alembic.ini /etc/pagure/alembic.ini
COPY files/pagure-* /usr/bin/
COPY files/service /etc/pagure/
RUN chmod +x /usr/bin/pagure-*
RUN useradd git && \
    mkdir -p /home/git/releases && \
    mkdir -p /home/git/pesudo_folder && \
    mkdir -p /home/git/remote_git_folder && \
    mkdir -p /home/git/gitolite && \
    mkdir -p /home/git/db && \
    chown git:git -R /var/log/pagure && \
    chown git:git -R /home/git
