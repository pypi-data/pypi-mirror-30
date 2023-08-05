import os
import yaml


from .exceptions import ConfigYamlReadError


def _read_config() -> str:
    """Read In Database Credentials

    This function will read in your connection details for
    connecting to Postgres from a `config.yaml` file. After doing so,
    it uses each part to generate the DSN. This DSN is then passed
    through to `asyncpg` in order to connect without having to manually
    enter your credentials everytime.
    """
    current_dir = os.path.abspath(os.curdir)
    file_path = os.path.join(current_dir, 'config.yaml')

    try:
        with open(file_path, mode='r', encoding='UTF-8') as file:
            config = yaml.load(file)
            dsn = f'postgresql://{config["user"]}:{config["password"]}@{config["host"]}:{config["port"]}/{config["database"]}'
            return dsn
    except ConfigYamlReadError as e:
        print("""
        Could not find configuration file `config.yaml` in current directory.

        Default format is:
        ==================

        database: '<datbase name>'
        host: '<host address>'
        port: '<database port>'
        user: '<username>'
        password: '<database password>'
        """)
        raise
