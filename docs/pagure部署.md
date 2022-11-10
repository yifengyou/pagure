# pagure部署


部署参看容器化部署中的 pagure-init

有不少细节主要注意。。处处有坑

1. 注意修改/tmp目录，默认mirror功能会在/tmp目录克隆，/tmp目录可用容量肯定要大于仓库容量，否则无法镜像成功
2. 


```
mount -t tmpfs -o size=8G tmpfs /tmp || true

mkdir -p /etc/pagure || true
mkdir -p /var/log/pagure || true
mkdir -p /home/git/releases || true
mkdir -p /home/git/pesudo_folder || true
mkdir -p /home/git/remote_git_folder || true
mkdir -p /home/git/db || true

# close registration email confirm
sed -i 's/user.token = token/user.token = ""/g' /usr/lib/python3.6/site-packages/pagure/ui/login.py

chown git:git -R /var/log/pagure
chown git:git -R /home/git

systemctl disable --now firewalld &> /dev/null || true
setenforce 0 &> /dev/null || true
getenforce

# init gitolite
if [ ! -f /home/git/.ssh/admin.pub ]
then
    su git -c "cd /home/git ; git config --global init.defaultBranch master"
    su git -c "cd /home/git ; ssh-keygen -f /home/git/.ssh/admin -t rsa -N ''"
    su git -c "cd /home/git ; gitolite setup -pk /home/git/.ssh/admin.pub "
    #su git -c "cd /home/git ; gitolite compile && HOME=/home/git/ gitolite trigger POST_COMPILE"
fi

if [ ! -f /home/git/db/pagure_dev.sqlite ]
then
    su git -c "python3 /usr/share/pagure/pagure_createdb.py  -c /etc/pagure/pagure.cfg -i /etc/pagure/alembic.ini"
fi

systemctl daemon-reload
systemctl enable --now pagure_worker.service pagure_gitolite_worker.service pagure_docs_web pagure_web pagure_mirror
systemctl enable --now pagure_mirror_project_in.timer
systemctl enable --now redis nginx sshd

for srv in `cat /etc/pagure/service`
do
    status $srv
done
netstat -anpt |grep 8880


cat >> ~/.bashrc << EOF
# github.com/yifengyou/bash
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
alias grep='grep --color=auto'
alias l.='ls -d .* -a --color=auto'
alias ll='ls -l -h -a --color=auto'
alias ls='ls -a --color=auto'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias xzegrep='xzegrep --color=auto'
alias xzfgrep='xzfgrep --color=auto'
alias xzgrep='xzgrep --color=auto'
alias zegrep='zegrep --color=auto'
alias zfgrep='zfgrep --color=auto'
alias zgrep='zgrep --color=auto'
alias push='git push'

export PROMPT_COMMAND="history -a"
export HISTTIMEFORMAT="%F %T "
export HISTSIZE=10000

PS1='\[\e[32;1m\][\[\e[31;1m\]\u\[\e[33;1m\]@\[\e[35;1m\]\h\[\e[36;1m\] \w\[\e[32;1m\]]\[\e[37;1m\]\$\[\e[0m\] '
EOF

# disable gitolite auth
sed -i 's/_die $ret/#_die $ret/g' /usr/share/gitolite3/gitolite-shell

cp ~/.bashrc /home/git/.bashrc

```































---
