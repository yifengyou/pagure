# pagure容器化部署


## 构建容器镜像

执行 0.build.sh

```
docker build -t rockylinux8.6-pagure .
```

## 运行容器

```
#!/bin/bash

set -e

docker container prune -f

[ ! -d home-git ] && mkdir home-git

docker run --privileged -d -v `pwd`/home-git:/home/git -p 8880:8880 -p 8822:22 --name rocky8.6-pagure rockylinux8.6-pagure /usr/sbin/init

echo "All done!"
```

## 初始化pagure


![20221018_110920_50](image/20221018_110920_50.png)

attach 到容器，执行pagure-init


## 浏览器访问

```
http://localhost:8880
```

localhost根据实际配置修改

![20221018_111018_86](image/20221018_111018_86.png)

![20221018_111554_24](image/20221018_111554_24.png)





# 效果


![20221018_110610_99](image/20221018_110610_99.png)

![20221018_110629_48](image/20221018_110629_48.png)



---
