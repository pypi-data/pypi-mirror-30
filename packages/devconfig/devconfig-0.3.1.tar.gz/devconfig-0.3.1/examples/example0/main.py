import devconfig
import defaults as config
if __name__ == '__main__':
    assert config.websources['google'].scheme == 'http'
    assert config.websources['google'](scheme='https').sub('images/') == 'https://www.google.com/images/'