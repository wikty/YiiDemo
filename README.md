## 创建 Yii 模板项目的工具

该项目用于创建 Yii 模板项目，可以快速地自定义项目的生成。

自定义 Yii 项目的大概流程如下：

1. 获取 Yii 源码
2. 为项目配置组件等参数
3. 运行命令生成项目

### Yii 源码

从官网[下载](https://www.yiiframework.com/) Yii 源码，将其放在项目 `src` 目录中，源码目录名按照 Yii 版本号来命名。

`src` 目录除了放置 Yii 源码外，还可以放置常用的一些自定义类、函数等代码，如项目在 `src/common` 中就存放了若干常用代码文件。

### 配置项目

关于项目的配置都写入到了 `config.py` 文件中，一般只需要配置该文件中的 `components` 即可，详见该文件。

### 生成项目

运行命令： `python main.py [project] [description] -v [version]`

其中各个参数解释如下：

* `project` 用于指定项目名称，该名称将作为 Yii 项目的 `config/web.php` 文件中 `$config['id']` 的取值。
* `description` 用于指定项目的描述信息。
* `version` 用于指定项目所依赖的 Yii 源码版本。

在运行以上命令后将会在当前目录的 `build` 文件夹中生成项目。项目的构建日志可以查看 `running.log`。

要为项目安装依赖的第三方库，需要切换到项目目录，然后运行：`composer update`。

安装完成后，可以运行 Yii 自带的服务器，检查项目是否常见成功，运行：`php yii serve --port 1234`。

