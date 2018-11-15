## 快速创建 Yii 项目的工具

该项目用于创建 Yii 项目原型，可以快速地自定义项目的生成。

自定义 Yii 项目的大概流程如下：

1. 获取 Yii 源码
2. 为项目配置组件等参数
3. 运行命令生成项目

### Yii 源码

从官网[下载](https://www.yiiframework.com/) Yii 源码，将其放在项目 `src` 目录中，源码目录名按照 Yii 版本号来命名。

`src` 目录除了放置 Yii 源码外，还可以放置常用的一些自定义类、函数等代码，如项目在 `src/common` 中就存放了若干常用代码文件。

### 配置项目

关于项目的配置都写入到了 `config.py` 文件中，一般只需要配置该文件中的 `components` 即可，详见该文件。或者也可以通过 `components.json` 来对此项进行配置，这样可以避免改写代码文件。

### 生成项目

运行命令： `python main.py create [project] [description] -v [version]`

其中各个参数解释如下：

* `project` 用于指定项目名称，该名称将作为 Yii 项目的 `config/web.php` 文件中 `$config['id']` 的取值。
* `description` 用于指定项目的描述信息。
* `version` 用于指定项目所依赖的 Yii 源码版本。

在运行以上命令后将会在当前目录的 `build` 文件夹中生成项目。项目的构建日志可以查看 `running.log`。

要为项目安装依赖的第三方库，需要切换到项目目录，然后运行：`composer update`。

安装完成后，可以运行 Yii 自带的服务器，检查项目是否常见成功，运行：`php yii serve --port 1234`。

### 部署项目

一般我们在本地会有一个开发环境和一个测试环境。

正常的流程是：

1. 在开发环境下，开发项目的功能
2. 将开发环境的项目推送到测试环境，进行测试
3. 测试完毕后，再将项目推送到生产环境中

使用本项目的部署功能可以快速创建开发和测试项目，运行命令：`python main.py deploy [project] [dev-repo] [test-repo] -a [apache] -n [hostname]`

其中各个参数解释如下：

* `project` 要进行部署的项目名称，注：该项目需要先生成好后才能进行部署
* `dev-repo` 指定开发项目的仓库路径。
* `test-repo` 指定测试项目的仓库路径，注：该路径一般位于 Web 服务器可以访问的目录中。
* `apache` 指定是否需要生成 Apache 虚拟主机配置信息。
* `hostname` 指定 Apache 虚拟主机的主机名，注：可以同时指定主机名和别名，用 `;` 来分割开。

创建完成开发和测试项目后，需要自己手动为测试项目配置虚拟主机。以后每当需要将开发项目推送到测试项目时：

1. 如果第三方库有更新，则需要运行：`composer update` 为开发项目更新第三方库。
2. 用 Git 提价代码，并推送到测试仓库：`git push local master`

