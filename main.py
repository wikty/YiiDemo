import os
import json
import shutil
import logging
import argparse
import subprocess

import config
from utils import CodeLines, id_generator, copyfile


def copy_src(src_root, dst_root, src_exclude=[]):
    # check Yii source
    if not os.path.exists(src_root):
        raise Exception('The Yii source not exists: {}'.format(src_root))
    for dirname in ['controllers', 'models', 'views', 'web']:
        if not os.path.exists(os.path.join(src_root, dirname)):
            raise Exception('This is an invalid Yii source: {}'.format(src_root))    
    # remove project directory
    if os.path.exists(dst_root):
        try:
            shutil.rmtree(dst_root)
        except Exception as e:
            print(e)
            print('There are somethig wrong!')
            print('Please manually delete the project build directory: {}!'.format(
                dst_root))
    # copy Yii source to project
    shutil.copytree(src_root, dst_root, 
                    ignore=shutil.ignore_patterns(*src_exclude))

def copy_common(dst_root, params={}):
    if params.get('required'):
        copyfile(params['src_path'], 
                 os.path.join(dst_root, params['dst_path']))
        return
    for key in params:
        if not isinstance(params[key], dict):
            continue
        copy_common(dst_root, params[key])

def update_site_component(file, params={}):
    if params.get('required'):
        return False
    
    cl = CodeLines()
    cl.add_text(r"""
namespace app\controllers;

use Yii;
use yii\filters\AccessControl;
use yii\web\Controller;
use yii\web\Response;
use yii\filters\VerbFilter;


class SiteController extends Controller
{
    /**
     * {@inheritdoc}
     */
    public function actions()
    {
        return [
            'error' => [
                'class' => 'yii\web\ErrorAction',
            ],
            'captcha' => [
                'class' => 'yii\captcha\CaptchaAction',
                'fixedVerifyCode' => YII_ENV_TEST ? 'testme' : null,
            ],
        ];
    }

    /**
     * Displays homepage.
     *
     * @return string
     */
    public function actionIndex()
    {
        echo 'hello world!';
    }
}""")
    cl.save(file)
    return True


def update_db_component(file, params={}):
    if not params.get('required'):
        return False

    cl = CodeLines()
    cl.add_lines([
        (r"return [", 0),
        (r"'class' => 'yii\db\Connection',", 1),
        (r"'dsn' => 'mysql:host={host};port={port};dbname={dbname}',".format(
            host=params['host'], 
            port=params['port'], 
            dbname=params['dbname']), 1),
        (r"'username' => '{username}',".format(
            username=params['username']), 1),
        (r"'password' => '{password}',".format(
            password=params['password']), 1),
        (r"'charset' => '{charset}',".format(
            charset=params['charset']), 1),
        (r"", 1),
        (r"// Schema cache options (for production environment)", 1),
        (r"//'enableSchemaCache' => true,", 1),
        (r"//'schemaCacheDuration' => 60,", 1),
        (r"//'schemaCache' => 'cache',", 1),
        (r"];", 0)
    ])
    cl.save(file)
    return True

def update_redis_component(file, params={}):
    if not params.get('required'):
        return False

    cl = CodeLines()
    cl.add_lines([
        (r"return [", 0),
        (r"'class' => 'yii\redis\Connection',", 1),
        (r"'hostname' => '{hostname}',  // change it to your redis server hostname".format(
            hostname=params['hostname']), 1),
        (r"'port' => {port},  // change it to your redis server port".format(
            port=params['port']), 1),
        (r"'database' => {database},  // which redis database you want to use".format(
            database=params['database']), 1),
        (r"{comment}'password' => '{password}',  // -> change it if redis requires password".format(
            comment=('' if params.get('password') else '// '), password=params.get('password', '')), 1),
        (r"];", 0)
    ])
    cl.save(file)
    return True

def update_composer_component(file, project, description, params={}):
    if not params.get('required'):
        return False

    with open(file, 'r+', encoding='utf8') as f:
        obj = json.load(f)
        obj['name'] = project
        obj['description'] = description
        obj['require'].update(params.get('require', {}))
        f.seek(0)
        json.dump(obj, f, indent=4)
    return True

def update_web_index(file, params={}):
    if params.get('utils', {}).get('required'):
        require_scripts = r"require __DIR__ . '/../common/Utils.php';"
    else:
        require_scripts = ''
    cl = CodeLines()
    cl.add_text(r"""
// comment out the following two lines when deployed to production
defined('YII_DEBUG') or define('YII_DEBUG', true);
defined('YII_ENV') or define('YII_ENV', 'dev');

require __DIR__ . '/../vendor/autoload.php';
require __DIR__ . '/../vendor/yiisoft/yii2/Yii.php';
{require}

$config = require __DIR__ . '/../config/web.php';

(new yii\web\Application($config))->run();""".format(require=require_scripts))
    cl.save(file)
    return True

def update_web_config(file, project, components={}):
    redis_required = components.get('redis', {}).get('required', False)
    site_required = components.get('site', {}).get('required', False)
    log_target = components.get('log', {}).get('target', 'file')
    log_class = components.get('log', {}).get('class', r'yii\log\FileTarget')
    cl = CodeLines()
    # require
    cl.add_line(r"$params = require __DIR__ . '/params.php';")
    cl.add_line(r"$db = require __DIR__ . '/db.php';")
    if redis_required:
        cl.add_line(r"$redis = require __DIR__ . '/redis.php';")
    # config
    cl.add_line(r"")
    cl.add_line(r"$config = [")
    cl.add_text(r"""
    'id' => '{project}',
    'basePath' => dirname(__DIR__),
    'bootstrap' => ['log'],
    'aliases' => [
        '@bower' => '@vendor/bower-asset',
        '@npm'   => '@vendor/npm-asset',
    ],""".format(project=project))
    cl.add_line(r"'components' => [", 1)
    # request component
    cl.add_line(r"'request' => [", 2)
    cl.add_line(r"// !!! insert a secret key in the following (if it is empty) - this is required by cookie validation", 2)
    cl.add_line(r"'cookieValidationKey' => '{secret}',".format(
        secret=id_generator(32)), 3)
    cl.add_line(r"],", 2)
    # cache component
    cl.add_line(r"'cache' => [", 2)
    if not redis_required:
        cl.add_line(r"'class' => 'yii\caching\FileCache',", 3)
    else:
        cl.add_line(r"// 'class' => 'yii\caching\FileCache',", 3)
        cl.add_line(r"'class' => 'yii\redis\Cache',", 3)
    cl.add_line(r"],", 2)
    # user, errorHandler, mailer components
    cl.add_text(r"""
        'user' => [
            'identityClass' => 'app\models\User',
            'enableAutoLogin' => true,
        ],
        'errorHandler' => [
            'errorAction' => 'site/error',
        ],
        'mailer' => [
            'class' => 'yii\swiftmailer\Mailer',
            // send all mails to a file by default. You have to set
            // 'useFileTransport' to false and configure a transport
            // for the mailer to send real emails.
            'useFileTransport' => true,
        ],""")
    # log component
    cl.add_line(r"'log' => [", 2)
    cl.add_line(r"'traceLevel' => YII_DEBUG ? 3 : 0,", 3)
    cl.add_line(r"'flushInterval' => YII_DEBUG ? 1 : 1000,", 3)
    cl.add_line(r"'targets' => [", 3)
    cl.add_line(r"[", 4)
    cl.add_line(r"'exportInterval' => YII_DEBUG ? 1 : 1000,", 5)
    if log_target == 'db':
        cl.add_line(r"// The default log target", 5)
        cl.add_line(r"// 'class' => 'yii\log\FileTarget',", 5)
        cl.add_line(r"// 'levels' => ['error', 'warning'],", 5)
        cl.add_line(r"// Database log target", 5)
        cl.add_line(r"'class' => '{cls}',".format(cls=log_class), 5)
        cl.add_line(r"'levels' => YII_DEBUG ? ['error', 'warning', 'info', 'trace', 'profile'] : ['error', 'warning'],", 5)
    else:
        cl.add_line(r"// The default log target")
        cl.add_line(r"'class' => 'yii\log\FileTarget',", 5)
        cl.add_line(r"'levels' => ['error', 'warning'],", 5)
    cl.add_line(r"],", 4)
    cl.add_line(r"],", 3)
    cl.add_line(r"],", 2)
    # urlManager component
    cl.add_line(r"'urlManager' => [", 2)
    cl.add_line(r"'enablePrettyUrl' => true,", 3)
    cl.add_line(r"'showScriptName' => false,", 3)
    cl.add_line(r"'enableStrictParsing' => false,", 3)
    cl.add_line(r"'rules' => [", 3)
    if not site_required:
        cl.add_line(r"'site/<action:.*+>' => 'site/index'", 4)
    cl.add_line(r"// '<controller:.+>/<action:.+>' => '<controller>/<action>',", 4)
    cl.add_line(r"],", 3)
    cl.add_line(r"],", 2)
    # db component
    cl.add_line(r"'db' => $db,", 2)
    # redis component
    if redis_required:
        cl.add_line(r"'redis' => $redis,", 2)
    cl.add_line(r"],", 1)
    cl.add_line(r"'params' => $params,", 1)
    cl.add_line(r"];")
    cl.add_line(r"")
    # environment settings
    cl.add_text(r"""if (YII_ENV_DEV) {
    // configuration adjustments for 'dev' environment
    $config['bootstrap'][] = 'debug';
    $config['modules']['debug'] = [
        'class' => 'yii\debug\Module',
        // uncomment the following to add your IP if you are not connecting from localhost.
        //'allowedIPs' => ['127.0.0.1', '::1'],
    ];

    $config['bootstrap'][] = 'gii';
    $config['modules']['gii'] = [
        'class' => 'yii\gii\Module',
        // uncomment the following to add your IP if you are not connecting from localhost.
        //'allowedIPs' => ['127.0.0.1', '::1'],
    ];
}""")
    cl.add_line(r"")
    # return config
    cl.add_line(r"return $config;")
    cl.save(file)
    return True

def run_composer(dst_root):
    result = subprocess.run(["composer", "update"], 
        cwd=dst_root,
        shell=True,
        capture_output=True)
    return result.stdout, result.stderr

def get_logger(log_file='running.log'):
    # create logger
    logger = logging.getLogger('YiiDemo')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_file)
    # fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    # ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def run(project, description, version):
    logger = get_logger()
    src_root = os.path.join(config.src_path, version)
    dst_root = os.path.join(config.dst_path, project)
    web_index_file = os.path.join(dst_root, config.web_index_file)
    web_config_file = os.path.join(dst_root, config.web_config_file)
    db_config_file = os.path.join(dst_root, config.db_config_file)
    redis_config_file = os.path.join(dst_root, config.redis_config_file)
    composer_config_file = os.path.join(dst_root, config.composer_config_file)
    site_controller_file = os.path.join(dst_root, config.site_controller_file)
    
    logger.info('Starting create the project [{}]: "{}"'.format(
        project, description))

    logger.info('Copy Yii {} source to create a new project'.format(project))
    copy_src(src_root, dst_root, config.src_exclude)
    logger.info('Yii source has been copied!')
    
    logger.info('Copy common source to the project'.format(project))
    copy_common(dst_root, config.src_common_params)
    logger.info('Common source has been copied!')

    logger.info('Updating the site component...')
    result = update_site_component(site_controller_file, 
                                   config.components['site'])
    logger.info('The site component updated: {}'.format(result))

    logger.info('Updating the db component...')
    result = update_db_component(db_config_file, 
                                 config.components['db'])
    logger.info('The db component updated: {}'.format(result))

    logger.info('Updating the redis component...')
    result = update_redis_component(redis_config_file, 
                                    config.components['redis'])
    logger.info('The redis component updated: {}'.format(result))

    logger.info('Updating the composer component...')
    result = update_composer_component(composer_config_file, 
                                       project, 
                                       description, 
                                       config.components['composer'])
    logger.info('The composer component updated: {}'.format(result))

    logger.info('Updating the `web/index.php` file...')
    update_web_index(web_index_file, config.src_common_params)
    logger.info('The file `web/index.php` has been updated!')

    logger.info('Updating the `config/web.php` file...')
    update_web_config(web_config_file, project, config.components)
    logger.info('The file `config/web.php` has been updated!')
    
    # result = run_composer(dst_root)
    # print(result)

    logger.info('The project [{}] has been successfully created!'.format(project))
    logger.info('Please run: `cd build/{} && composer update` to\
 install packages for your project'.format(project))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create Yii new project.')
    parser.add_argument('project',
                        help='The name of project.')
    parser.add_argument('description',
                        help='The description of project')
    parser.add_argument('-v', 
                        dest='version',
                        default=config.src_version,
                        help='The Yii version to create project.')

    args = parser.parse_args()
    run(args.project, args.description, args.version)
    
    
    