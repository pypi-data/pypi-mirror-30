import click
from flask_socketio import SocketIO

from cbc_api.app import app
from cbc_api.config_manager import ConfigManager

@click.group()
def main():
    """
    Welcome to the DataKind/CBC CLI! :)
    To learn more about a command, type the command and the --help flag
    """
    pass

@click.command('launch', help='Launches the API')
@click.option('--debug', is_flag=True, help='Runs in debug mode if True')
def launch(debug):
    """
    Launches the API at https://localhost:5000/
    """
    socketio = SocketIO(app)
    socketio.run(app, debug=debug)
main.add_command(launch)

@click.command('add_config', help='Adds a new configuration')
@click.option('--key', help='The key for the config')
@click.option('--value', help='The value for the config')
@click.option('--overwrite', is_flag=True, help='Overwrites existing config if true')
def add_config(key, value, overwrite):
    """
    Adds a new configuration
    """
    config_manager = ConfigManager()
    config_manager.add_config(key=key, value=value, overwrite=overwrite)
main.add_command(add_config)

@click.command('update_config', help='Updates a configuration')
@click.option('--key', help='The key for the config')
@click.option('--value', help='The value for the config')
def update_config(key, value):
    """
    Updates a new configuration
    """
    config_manager = ConfigManager()
    config_manager.update_config(key=key, value=value)
main.add_command(update_config)

@click.command('delete_config', help='Deletes a configuration')
@click.option('--key', help='The key for the config')
def delete_config(key):
    """
    Deletes a new configuration
    """
    config_manager = ConfigManager()
    config_manager.delete_config(key=key)
main.add_command(delete_config)

@click.command('list_configs', help='Lists exsiting configs')
def list_configs():
    """
    Lists existing configs
    """
    config_manager = ConfigManager()
    config_manager.list_configs()
main.add_command(list_configs)

@click.command('get_config', help='Retreives an exsiting configs')
@click.option('--key', help='The key for the config')
def get_config(key):
    """
    Lists existing configs
    """
    config_manager = ConfigManager()
    value = config_manager.get_config(key)
main.add_command(get_config)

if __name__ == '__main__':
    main()
