import os
import json
import shutil


from utils import CodeLines, id_generator, copyfile, tpl


site_controller_code = r"""
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
}"""


db_component_code = r"""
return [
    'class' => 'yii\db\Connection',
    'dsn' => 'mysql:host={{hostname}};port={{port}};dbname={{database}}',
    'username' => '{{username}}',
    'password' => '{{password}}',
    'charset' => '{{charset}}',
    
    // Schema cache options (for production environment)
    //'enableSchemaCache' => true,
    //'schemaCacheDuration' => 60,
    //'schemaCache' => 'cache',
];"""


redis_component_code = r"""
return [
    'class' => 'yii\redis\Connection',
    'hostname' => '{{hostname}}',  // change it to your redis server hostname
    'port' => {{port}},  // change it to your redis server port
    'database' => {{database}},  // which redis database you want to use
    {{password}}
];"""


web_index_code = r"""
// comment out the following two lines when deployed to production
defined('YII_DEBUG') or define('YII_DEBUG', true);
defined('YII_ENV') or define('YII_ENV', 'dev');

require __DIR__ . '/../vendor/autoload.php';
require __DIR__ . '/../vendor/yiisoft/yii2/Yii.php';
{{require}}

$config = require __DIR__ . '/../config/web.php';

(new yii\web\Application($config))->run();"""


web_config_code = r"""
$params = require __DIR__ . '/params.php';
{{require}}

$config = [
    'id' => '{{project}}',
    'basePath' => dirname(__DIR__),
    'bootstrap' => ['log'],
    'aliases' => [
        '@bower' => '@vendor/bower-asset',
        '@npm'   => '@vendor/npm-asset',
    ],
    'components' => [
        'request' => [
        // !!! insert a secret key in the following (if it is empty) - this is required by cookie validation
            'cookieValidationKey' => '{{secret}}',
        ],
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
        ],
{{components}}
    ],
    'params' => $params,
];

if (YII_ENV_DEV) {
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
}

return $config;"""


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
    cl.add_text(site_controller_code)
    cl.save(file)
    return True


def update_db_component(file, params={}):
    if not params.get('required'):
        return False
    cl = CodeLines()
    cl.add_text(tpl(db_component_code, 
        hostname=params['hostname'],
        port=params['port'],
        database=params['database'],
        username=params['username'],
        password=params['password'],
        charset=params['charset']))
    cl.save(file)
    return True


def update_redis_component(file, params={}):
    if not params.get('required'):
        return False
    cl = CodeLines()
    cl.add_text(tpl(redis_component_code, 
        hostname=params['hostname'],
        port=params['port'],
        database=params['database'],
        password=r"{comment}'password' => '{password}',  // -> change it if redis requires password".format(
            comment=('' if params.get('password') else '// '), password=params.get('password', ''))))
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
    require_scripts = ''
    if params.get('utils', {}).get('required'):
        require_scripts = r"require __DIR__ . '/../common/Utils.php';"        
    cl = CodeLines()
    cl.add_text(tpl(web_index_code, require=require_scripts))
    return True


def update_web_config(file, project, components={}):
    db_required = components.get('db', {}).get('required', False)
    redis_required = components.get('redis', {}).get('required', False)
    site_required = components.get('site', {}).get('required', False)
    log_target = components.get('log', {}).get('target', 'file')
    log_class = components.get('log', {}).get('class', r'yii\log\FileTarget')
    
    ccl = CodeLines(start_line='')
    # cache component
    ccl.add_line(r"'cache' => [")
    if not redis_required:
        ccl.add_line(r"'class' => 'yii\caching\FileCache',", 1)
    else:
        ccl.add_line(r"// 'class' => 'yii\caching\FileCache',", 1)
        ccl.add_line(r"'class' => 'yii\redis\Cache',", 1)
    ccl.add_line(r"],")
    # log component
    ccl.add_line(r"'log' => [")
    ccl.add_line(r"'traceLevel' => YII_DEBUG ? 3 : 0,", 1)
    ccl.add_line(r"'flushInterval' => YII_DEBUG ? 1 : 1000,", 1)
    ccl.add_line(r"'targets' => [", 1)
    ccl.add_line(r"[", 2)
    ccl.add_line(r"'exportInterval' => YII_DEBUG ? 1 : 1000,", 3)
    if log_target == 'db':
        ccl.add_line(r"// The default log target", 3)
        ccl.add_line(r"// 'class' => 'yii\log\FileTarget',", 3)
        ccl.add_line(r"// 'levels' => ['error', 'warning'],", 3)
        ccl.add_line(r"// Database log target", 3)
        ccl.add_line(r"'class' => '{cls}',".format(cls=log_class), 3)
        ccl.add_line(r"'levels' => YII_DEBUG ? ['error', 'warning', 'info', 'trace', 'profile'] : ['error', 'warning'],", 5)
    else:
        ccl.add_line(r"// The default log target")
        ccl.add_line(r"'class' => 'yii\log\FileTarget',", 3)
        ccl.add_line(r"'levels' => ['error', 'warning'],", 3)
    ccl.add_line(r"],", 2)
    ccl.add_line(r"],", 1)
    ccl.add_line(r"],")
    # urlManager component
    ccl.add_line(r"'urlManager' => [")
    ccl.add_line(r"'enablePrettyUrl' => true,", 1)
    ccl.add_line(r"'showScriptName' => false,", 1)
    ccl.add_line(r"'enableStrictParsing' => false,", 1)
    ccl.add_line(r"'rules' => [", 1)
    if not site_required:
        ccl.add_line(r"'site/<action:.*+>' => 'site/index'", 2)
    ccl.add_line(r"// '<controller:.+>/<action:.+>' => '<controller>/<action>',", 2)
    ccl.add_line(r"],", 1)
    ccl.add_line(r"],")
    # db component
    if db_required:
        ccl.add_line(r"'db' => $db,")
    # redis component
    if redis_required:
        ccl.add_line(r"'redis' => $redis,")
    # web config code
    cl = CodeLines()
    require_scripts = []
    if db_required:
        require_scripts.append(r"$db = require __DIR__ . '/db.php';")
    if redis_required:
        require_scripts.append(r"$redis = require __DIR__ . '/redis.php';")
    cl.add_text(tpl(web_config_code, 
        require='\n'.join(require_scripts), 
        project=project,
        secret=id_generator(32),
        components='\n'.join(ccl.dump(2))))
    cl.save(file)
    return True