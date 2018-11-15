import os
import json
import argparse
import subprocess

import config
import create_project
from utils import get_logger, merge_dict


def run_composer(dst_root):
    result = subprocess.run(["composer", "update"], 
        cwd=dst_root,
        shell=True,
        capture_output=True)
    return result.stdout, result.stderr


def run_create_project(project, description, version):
    logger = get_logger()
    src_root = os.path.join(config.src_path, version)
    dst_root = os.path.join(config.dst_path, project)
    web_index_file = os.path.join(dst_root, config.web_index_file)
    web_config_file = os.path.join(dst_root, config.web_config_file)
    db_config_file = os.path.join(dst_root, config.db_config_file)
    redis_config_file = os.path.join(dst_root, config.redis_config_file)
    composer_config_file = os.path.join(dst_root, config.composer_config_file)
    site_controller_file = os.path.join(dst_root, config.site_controller_file)
    
    components_file = config.components_file
    if os.path.isfile(components_file):
        data = {}
        with open(components_file, 'r') as f:
            data = json.load(f)
        config.components = merge_dict(config.components, data)
    
    logger.info('Starting create the project [{}]: "{}"'.format(
        project, description))

    logger.info('Copy Yii {} source to create a new project'.format(project))
    create_project.copy_src(src_root, dst_root, config.src_exclude)
    logger.info('Yii source has been copied!')
    
    logger.info('Copy common source to the project'.format(project))
    create_project.copy_common(dst_root, config.src_common_params)
    logger.info('Common source has been copied!')

    logger.info('Updating the site component...')
    result = create_project.update_site_component(site_controller_file, 
                                   config.components['site'])
    logger.info('The site component updated: {}'.format(result))

    logger.info('Updating the db component...')
    result = create_project.update_db_component(db_config_file, 
                                 config.components['db'])
    logger.info('The db component updated: {}'.format(result))

    logger.info('Updating the redis component...')
    result = create_project.update_redis_component(redis_config_file, 
                                    config.components['redis'])
    logger.info('The redis component updated: {}'.format(result))

    logger.info('Updating the composer component...')
    result = create_project.update_composer_component(composer_config_file, 
                                       project, 
                                       description, 
                                       config.components['composer'])
    logger.info('The composer component updated: {}'.format(result))

    logger.info('Updating the `web/index.php` file...')
    create_project.update_web_index(web_index_file, config.src_common_params)
    logger.info('The file `web/index.php` has been updated!')

    logger.info('Updating the `config/web.php` file...')
    create_project.update_web_config(web_config_file, project, config.components)
    logger.info('The file `config/web.php` has been updated!')
    
    # result = run_composer(dst_root)
    # print(result)

    logger.info('The project [{}] has been successfully created!'.format(project))
    logger.info('Please run: `cd build/{} && composer update` to\
 install packages for your project'.format(project))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create Yii new project.')
    subparsers = parser.add_subparsers(title='Create and Deploy',
                                       dest='subcmd', 
                                       help="Create and deploy your project.")
    create_parser = subparsers.add_parser('create', help='Create project.')
    create_parser.add_argument('project',
                                help='The name of project.')
    create_parser.add_argument('description',
                                help='The description of project.') 
    create_parser.add_argument('-v', 
                               dest='version',
                               default=config.src_version,
                               help='The Yii source version to create project.')
    
    deploy_parser = subparsers.add_parser('deploy', help='Deploy project.')
    deploy_parser.add_argument('project',
                               help='The name of project.')
    deploy_parser.add_argument('dev-repo', 
                               help='The path of development repository.')
    deploy_parser.add_argument('test-repo', 
                               help='The path of test repository.')
    deploy_parser.add_argument('-a',
                               dest='apache',
                               type=bool,
                               default=True,
                               help='Output the virtual host settings for Apache.')

    args = parser.parse_args()
    if args.subcmd == 'create':
        run_create_project(args.project, args.description, args.version)
    elif args.subcmd == 'deploy':
        pass
    
    
    