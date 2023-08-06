import devconfig
#devconfig.module_meta['mysql_configserver'] = JsonTableMetaLoader('mysql://configuser:configpassword@mysql.server:3306/config_database')
devconfig.merges['local_settings']._with('mysql_configserver.table_staging', 'module.defaults')


import local_settings as config

if __name__ == '__main__':
    assert config.websources['google']['images'].path == '/images/'
    assert config.websources['google']['search'].path == '/search_new/'
