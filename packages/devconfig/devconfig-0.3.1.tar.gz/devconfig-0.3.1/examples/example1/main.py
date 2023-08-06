import devconfig
devconfig.merges['local_settings']._with('module.defaults', 'django.conf.settings')

import local_settings as config
from module import defaults
from django.conf import settings

if __name__ == '__main__':
    assert config.websources['google']['images'].path == '/images/'
    assert config.websources['google']['search'].path == '/search_new/'
