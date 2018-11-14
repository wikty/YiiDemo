import os

dst_path = './build'  # the destination root path for new projects 

src_path = './src'  # the path of Yii sources
src_version = '2.0.14'  # the default version of Yii
src_exclude = ['vendor']  # the items'll be excluded from the Yii source

# source files
root_dir = ''
web_dir = 'web'
db_config_file = 'config/db.php'
redis_config_file = 'config/redis.php'
web_config_file = 'config/web.php'
web_index_file = 'web/index.php'
composer_config_file = 'composer.json'
site_controller_file = 'controllers/SiteController.php'

# the common code for projects
src_common_path = './src/common'
dst_common_path = 'common'
src_files_path = './src/files'
src_common_params = {
    'controllers': {
        'base': {
            'required': True,
            'src_path': os.path.join(src_common_path, 'controllers', 'BaseController.php'),
            'dst_path': os.path.join(dst_common_path, 'controllers', 'BaseController.php')
        }
    },
    'models': {
        'log': {
            'required': True,
            'src_path': os.path.join(src_common_path, 'models', 'Log.php'),
            'dst_path': os.path.join('models', 'Log.php')
        }
    },
    'log': {
        'db': {
            'required': True,
            'src_path': os.path.join(src_common_path, 'log', 'DbTarget.php'),
            'dst_path': os.path.join(dst_common_path, 'log', 'DbTarget.php')
        }
    },
    'const': {
        'required': True,
        'src_path': os.path.join(src_common_path, 'ConstCode.php'),
        'dst_path': os.path.join(dst_common_path, 'ConstCode.php')
    },
    'utils': {
        'required': True,
        'src_path': os.path.join(src_common_path, 'Utils.php'),
        'dst_path': os.path.join(dst_common_path, 'Utils.php')
    },
    'htaccess': {
        'required': True,  # add htaccess for apache
        'src_path': os.path.join(src_files_path, '.htaccess'),
        'dst_path': os.path.join(web_dir, '.htaccess')
    },
    'composer': {
        'required': True,  # install composer for project
        'src_path': os.path.join(src_files_path, 'composer.phar'),
        'dst_path': os.path.join(root_dir, 'composer.phar')
    }
}

# The components that you want to equip with the new project
components = {
    'site': {
        'required': False,  # set false to remove the default site controller
    },
    # make sure you have installed MySQL and run it
    'db': {
        'required': True,
        'host': 'db',  # change to your db server hostname
        'port': 3306,  # change to your db server port
        'dbname': 'foo',  # change to your the name of the database
        'username': 'root',  # change to your username of db
        'password': '',  # change to your password of db
        'charset': 'utf8'
    },
    # must include redis into the packages if you want to use it
    'redis': {
        'required': True,
        'hostname': 'redis',  # change to your redis server hostname
        'port': 6379,  # change to your redis server port
        'database': 0,  # the redis database you want to use
        'password': '',  # change it if redis requires password auth
    },
    # you must create the log table by yourself
    'log': {
        'required': True,
        'target': 'db', # or file
        'class': r'app\common\log\DbTarget', # or yii\log\FileTarget
    },
    # config for composer
    'composer': {
        'required': True,
        # the list of packages want to be installed by composer
        'require': {
            # Redis Cache, Session and ActiveRecord for the Yii framework
            "yiisoft/yii2-redis": "~2.0.0",
            # Flexible and feature-complete Redis client for PHP and HHVM
            # "predis/predis": "~1.1.1",

            
            # "bower-asset/bootstrap": "^3.3",
            # "bower-asset/materialize": "^0.97",
            # "npm-asset/jquery": "^2.2"
        }
    }
}