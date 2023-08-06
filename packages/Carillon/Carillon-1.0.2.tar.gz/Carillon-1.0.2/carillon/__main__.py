import signal
import os.path
import logging.config
import functools
import time
import sys
import argparse
import subprocess

import yaml
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

ETC_ROOT = os.path.join('/', 'etc', 'carillon')
CONFIG_ROOT = os.path.join(ETC_ROOT, 'conf.d')
USER_CONFIG = os.path.join(os.path.expanduser('~'), '.config', 'carillon')
SRC_ROOT = os.path.dirname(__file__)
WORKING_ROOT = os.getcwd()


class Application(object):
    """
    Catch-all class for running the keyboards application
    """

    def __init__(self):
        super(Application, self).__init__()
        self.is_running = True
        self.menu = Gtk.Menu()
        self.icon = Gtk.StatusIcon()
        self.icon.set_has_tooltip(True)
        self.icon.connect('popup-menu', self.on_popup_menu)
        self.icon.connect('query-tooltip', self.set_tooltip)
        self._all_keyboards = []
        self.keyboard = None

    def load(self, config_filename):
        """
        Loads the application state from the given configuration file name

        :param config_filename:
        """
        config_file_path = self.get_file_path(config_filename)
        with open(config_file_path) as handle:
            config_data = yaml.load(handle)

        configured_logging = config_data.get('logging', {})
        logging_conf = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
            },
            'handlers': {
                'file': {
                    'level': 'DEBUG',
                    'formatter': 'standard',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': configured_logging.get('file_path',
                                                       '/tmp/carillon.log'),
                    'maxBytes': 1024000,
                    'backupCount': 3
                },
                'console': {
                    'level': 'INFO',
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                },
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'file'],
                    'level': configured_logging.get('level', 'INFO')
                }
            }
        }
        logging.config.dictConfig(logging_conf)

        keyboards = config_data['keyboards']
        selected = config_data.get('selected', next(iter(keyboards.keys())))
        selected_keyboard = keyboards[selected]

        self.all_keyboards = keyboards
        menu_item = Gtk.MenuItem()
        menu_item.set_label('Quit')
        menu_item.connect('activate', self.shutdown)
        self.menu.append(menu_item)
        self.menu.show_all()
        self.set_keyboard(selected_keyboard)

    def on_popup_menu(self, icon, button, time):
        """
        Opens the popup menu for the given Gtk icon

        :param icon:
        :param button:
        :param time:
        :return:
        """
        def pos(menu, x, y, user_data):
            return Gtk.StatusIcon.position_menu(menu, x, y, user_data)
        self.menu.popup(None, None, pos, icon, button, time)

    def set_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        """
        Sets the tooltip for a Gtk tooltip
        :param widget:
        :param x:
        :param y:
        :param keyboard_mode:
        :param tooltip:
        :return:
        """
        tooltip.set_text(self.keyboard['name'])
        return True

    def get_file_path(self, filename):
        """
        Finds the given filename in one of the supported directories.
        These are:

        * current working directory
        * XDG config directory e.g. ~/.config/carillon
        * /etc/carillon/conf.d
        * /etc/carillon
        * directory of package install

        :param filename:
        :return: absolute file path to first matching filename, or None if
        no matching filename found
        """
        file_path = None
        for path in [WORKING_ROOT,
                     USER_CONFIG,
                     CONFIG_ROOT,
                     ETC_ROOT,
                     SRC_ROOT]:
            search_path = os.path.join(path, filename)
            if os.path.exists(search_path):
                file_path = search_path
                break
        if file_path is None:
            raise IOError('Failed to find system path for {}'.format(filename))
        return file_path

    @property
    def all_keyboards(self):
        """
        Returns the list of configured keyboards
        :return:
        """
        return self._all_keyboards

    @all_keyboards.setter
    def all_keyboards(self, value):
        """
        Sets the list of keyboards for the application, loading the icon menu
        based on the list.

        :param value:
        """
        if value != self._all_keyboards:
            self._all_keyboards = value
            for keyboard in sorted(self._all_keyboards.values(),
                                   key=lambda val: val['name']):
                menu_item = Gtk.MenuItem()
                menu_item.set_label(keyboard['name'])
                menu_item.connect(
                    'activate',
                    functools.partial(self.set_keyboard, keyboard)
                )
                self.menu.append(menu_item)

    def set_keyboard(self, new_keyboard, *args):
        """
        Sets the selected keyboard layout, updating UI and changing OS settings
        :param new_keyboard:
        :param args:
        """
        if self.keyboard != new_keyboard:
            logging.info('Selecting keyboard %s', new_keyboard['name'])
            self.keyboard = new_keyboard
            self.icon.set_from_file(
                self.get_file_path(os.path.join('icons', new_keyboard['icon'])))
            self.load_keyboard(new_keyboard)

    def load_keyboard(self, keyboard):
        """
        Loads the keyboard layout using OS system calls
        :param keyboard:
        """
        # uses setxkbmap which is as reliable as it gets for
        # setting keyboard layout in an X client/server environment
        set_args = ['setxkbmap',
                    '-model', keyboard['model'],
                    '-layout', keyboard['layout']]
        variant = keyboard.get('variant')
        if variant:
            set_args += ['-variant', variant]
        subprocess.check_call(set_args)

    def shutdown(self, *args):
        """
        Shuts down the application thread
        """
        logging.info('Shutting down')
        self.is_running = False

    def run(self, *args):
        """
        Runs the application, managing the main loop
        """
        Gtk.init(sys.argv)
        while self.is_running:
            time.sleep(0.01)
            Gtk.main_iteration()


def main():
    logging.info('Starting up')
    parser = argparse.ArgumentParser(
        description='Application to manage keyboard layouts')
    parser.add_argument('-c', '--config-file', default='default.yml')
    args = parser.parse_args()

    program = Application()
    signal.signal(signal.SIGTERM, program.shutdown)
    signal.signal(signal.SIGINT, program.shutdown)

    program.load(args.config_file)
    program.run()


if __name__ == '__main__':
    main()
