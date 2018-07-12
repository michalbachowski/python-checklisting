import os


def pytest_addoption(parser):
    parser.addoption(
        '--env',
        type=str,
        dest='envs',
        action='append',
        help='Add new env from command line. Each value should be in form env_name:env_value ' +
        '(env_name will be uppercased). You can specify the option multiple times (but with one env at a time!)')


def pytest_configure(config):
    envs = config.getoption('envs')
    if not envs:
        return
    for env in envs:
        (name, value) = str(env).split(':')
        os.environ[name.upper()] = value
