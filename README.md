# pagure项目解析

![20221006_090229_87](image/20221006_090229_87.png)


## 本仓库说明

1. pagure项目学习笔记

```
Something I hope you know before go into the coding~
* First, please watch or star this repo, I'll be more happy if you follow me.
* Bug report, questions and discussion are welcome, you can post an issue or pull a request.
```

## 目录

* [pagure介绍](docs/pagure介绍.md)
* [pagure部署](docs/pagure部署.md)
* [pagure容器化部署](docs/pagure容器化部署.md)
* [pagure源码分析](docs/pagure源码分析.md)
    * [镜像站点流程](docs/pagure源码分析/镜像站点流程.md)
    * [pygit2如何调用libgit2](docs/pagure源码分析/pygit2如何调用libgit2.md)
    * [API](docs/pagure源码分析/API.md)
        * [获取仓库分支信息](docs/pagure源码分析/API/获取仓库分支信息.md)

## pagure项目简介

![20210713_132216_59](image/20210713_132216_59.png)


* Pagure 这个名字取自法语单词“pagere”。法语中的 Pagure 被用作Paguroidea 超科甲壳类动物的通用名称，该超科基本上是寄居蟹的科。
* Paugre 是一个典型的git Server，类似于gitlab、github
* 基于gitolite、pygit2
* fedora、centos开源软件托管仓库


## 相关站点

* 官方地址：<https://pagure.io/pagure>
* 官方文档：<https://docs.pagure.org/pagure/index.html>
* GitHub加速地址：<https://hub.fastgit.org/yifengyou/learn-pagure.git>

## 图示

![20210626_223010_17](image/20210626_223010_17.png)

![20210626_223026_66](image/20210626_223026_66.png)


---
