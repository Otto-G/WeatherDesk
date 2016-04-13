#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import re
import textwrap

# Library to set wallpaper and find desktop - Cross-platform

# set_wallpaper() and get_config_dir()
# taken (and modified a bit) from http://stackoverflow.com/a/21213504/5413945
# by stackoverflow user Martin Hensen

# get_desktop_environment()
# taken (and modified a bit) from http://stackoverflow.com/a/21213358/5413945
# by stackoverflow user Martin Hensen

def get_desktop_environment():

    if sys.platform in ['win32', 'cygwin']: return 'windows'

    elif sys.platform == 'darwin': return 'mac'

    else:

        desktop_session = os.environ.get('DESKTOP_SESSION')

        if desktop_session is not None:

            desktop_session = desktop_session.lower()

            if desktop_session in ['gnome','unity', 'cinnamon', 'mate', 'xfce4', 'lxde', 'fluxbox',
                                   'blackbox', 'openbox', 'icewm', 'jwm', 'afterstep','trinity', 'kde']:

                return desktop_session

            #-- Special cases --#

            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
            # There is no guarantee that they will not do the same with the other desktop environments.

            elif 'xfce' in desktop_session or desktop_session.startswith('xubuntu'): return 'xfce4'

            elif desktop_session.startswith('ubuntu'): return 'unity'

            elif desktop_session.startswith('lubuntu'): return 'lxde'

            elif desktop_session.startswith('kubuntu'):  return 'kde'

            elif desktop_session.startswith('razor'): return 'razor-qt'

            elif desktop_session.startswith('wmaker'): return 'windowmaker'

        if os.environ.get('KDE_FULL_SESSION') == 'true':

            return 'kde'

        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):

            if not 'deprecated' in os.environ.get('GNOME_DESKTOP_SESSION_ID'):

                return 'gnome2'

        elif is_running('xfce-mcs-manage'): return 'xfce4'
        elif is_running('ksmserver'): return 'kde'

    return 'unknown'

def is_running(process):

    try:  # Linux/Unix

        s = subprocess.Popen(['ps', 'axw'],stdout=subprocess.PIPE)

    except:  # Windows

        s = subprocess.Popen(['tasklist', '/v'],stdout=subprocess.PIPE)

    for x in s.stdout:

        if re.search(process, x):

            return True

    return False

def set_wallpaper(image, img_format):

    if not img_format.startswith('.'): args.format = ''.join(('.', args.format))

    if not os.path.isdir(os.path.expanduser('~/Pictures/WeatherDesk/')): os.mkdir(os.path.expanduser('~/Pictures/WeatherDesk/'))

    current_image = open(
        os.path.join(
        os.path.expanduser('~'), str('Pictures/WeatherDesk/background' + img_format)
        ), 'w')

    current_image.close()

    desktop_env = get_desktop_environment()

    current_image_path = os.path.abspath(os.path.join(
    os.path.expanduser('~'), str('Pictures/WeatherDesk/background' + img_format)
    ))

    shutil.copyfile(image, current_image_path)

    try:

        if desktop_env in ['gnome', 'unity', 'cinnamon']:

            uri = 'file://%s' % current_image_path

            try:

                SCHEMA = 'org.gnome.desktop.background'
                KEY = 'picture-uri'
                gsettings = Gio.Settings.new(SCHEMA)

                gsettings.set_string(KEY, uri)

            except:

                args = ['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', uri]
                subprocess.Popen(args)

        elif desktop_env == 'mate':

            try: # MATE >= 1.6

                args = ['gsettings', 'set', 'org.mate.background', 'picture-filename', '%s' % current_image_path]
                subprocess.Popen(args)

            except: # MATE < 1.6

                args = ['mateconftool-2','-t','string','--set','/desktop/mate/background/picture_filename','%s' % current_image_path]
                subprocess.Popen(args)

        elif desktop_env == 'gnome2':

            args = ['gconftool-2','-t','string','--set','/desktop/gnome/background/picture_filename', '%s' % current_image_path]
            subprocess.Popen(args)

        elif desktop_env == 'kde': pass

            # The KDE 4+ method of changing *anything* in the CLI is either
            # non-existent or deprecated or horribly convoluted.
            # There have been long-open bugs (5 yrs and counting) but no fix.

            # There was *one* way (in KDE 4) - the file
            # ~/.kde/share/config/plasma-desktop-appletsrc
            # That too, is gone in KDE 5.

            # The only way seems to be to *make* the user set a file as
            # wallpaper and keep overwriting  that file. KDE will, apparently,
            # notice the change and update automatically.

            # Update: That, too, is gone. KDE users will have to set a
            # peridically updating slideshow in the ~/WeatherDesk folder.

            # Update: Even *that* does not work. Sorry, KDE.

        elif desktop_env in ['kde3', 'trinity']:

            args = 'dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % current_image_path
            subprocess.Popen(args,shell=True)

        elif desktop_env=='xfce4':

            # XFCE4's image property is not image-path but last-image (What?)
            # Only GNOME seems to have a sane wallpaper interface

            XFCE_SCRIPT = r'''
monitor_port=$(xrandr | grep -e " connected [^(]" | sed -e "s/\([A-Z0-9]\+\) connected.*/\1/")
xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor"$monitor_port"/workspace0/last-image -s ''' + current_image_path + '''\nxfdesktop --reload'''

            xfce_script_file = open(os.path.expanduser('~/.weatherdesk_script.sh'), 'w')

            xfce_script_file.truncate()

            xfce_script_file.write(XFCE_SCRIPT)

            xfce_script_file.close()

            subprocess.Popen(['sh', os.path.abspath(os.path.expanduser('~/.weatherdesk_script.sh'))])

        elif desktop_env=='razor-qt':

            desktop_conf = configparser.ConfigParser()
            # Development version

            desktop_conf_file = os.path.join(get_config_dir('razor'),'desktop.conf')

            if os.path.isfile(desktop_conf_file):

                config_option = r'screens\1\desktops\1\wallpaper'

            else:

                desktop_conf_file = os.path.join(os.path.expanduser('~'),'.razor/desktop.conf')
                config_option = r'desktops\1\wallpaper'

            desktop_conf.read(os.path.join(desktop_conf_file))

            try:

                if desktop_conf.has_option('razor',config_option):  # only replacing a value

                    desktop_conf.set('razor',config_option,current_image_path)

                    with codecs.open(desktop_conf_file, 'w', encoding='utf-8', errors='replace') as f:

                        desktop_conf.write(f)

            except: pass


        elif desktop_env in ['fluxbox','jwm','openbox','afterstep']:

            try:

                args = ['fbsetbg', current_image_path]
                subprocess.Popen(args)

            except:

                sys.stderr.write('Error: Failed to set wallpaper with fbsetbg!')
                sys.stderr.write('Please make sre that You have fbsetbg installed.')

        elif desktop_env == 'icewm':

            args = ['icewmbg', current_image_path]
            subprocess.Popen(args)

        elif desktop_env == 'blackbox':

            args = ['bsetbg', '-full', current_image_path]
            subprocess.Popen(args)

        elif desktop_env == 'lxde':

            args = 'pcmanfm --set-wallpaper %s --wallpaper-mode=scaled' % current_image_path
            subprocess.Popen(args,shell=True)

        elif desktop_env == 'windowmaker':

            args = 'wmsetbg -s -u %s' % current_image_path
            subprocess.Popen(args,shell=True)

        elif desktop_env=='enlightenment':

           args = 'enlightenment_remote -desktop-bg-add 0 0 0 0 %s' % current_image_path
           subprocess.Popen(args,shell=True)

        elif desktop_env == 'windows':

               WIN_SCRIPT = '''reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v Wallpaper /t REG_SZ /d  %s /f

rundll32.exe user32.dll,UpdatePerUserSystemParameters
''' % current_image_path

               win_script_file = open(os.path.abspath(os.path.expanduser('~/.weatherdesk_script.bat')), 'w')

               win_script_file.write(WIN_SCRIPT)

               win_script_file.close()

               subprocess.call([os.path.abspath(os.path.expanduser('~/.weatherdesk_script.bat'))], shell=True)

        elif desktop_env == 'mac':

            try:

               from appscript import app, mactypes

               app('Finder').desktop_picture.set(mactypes.File(current_image_path))

            except ImportError:

                OSX_SCRIPT = '''tell application 'Finder' to
set desktop picture to POSIX file '%s'
end tell
                ''' % current_image_path

                osx_script_file = open(os.path.expanduser('~/.weatherdesk_script.sh'), 'w')

                osx_script_file.truncate()

                osx_script_file.write(OSX_SCRIPT)

                osx_script_file.close()

                subprocess.Popen(['/usr/bin/osascript', os.path.abspath(os.path.expanduser('~/.weatherdesk_script.sh'))])
        else:

            sys.stderr.write('Error: Failed to set wallpaper. (Desktop not supported)')

            return False

        return True

    except:

        sys.stderr.write('Error: Failed to set wallpaper.')

        return False

def get_config_dir(app_name):

        if 'XDG_CONFIG_HOME' in os.environ:

            confighome = os.environ['XDG_CONFIG_HOME']

        elif 'APPDATA' in os.environ:  # On Windows

            confighome = os.environ['APPDATA']

        else:

            try:

                from xdg import BaseDirectory
                confighome =  BaseDirectory.xdg_config_home

            except ImportError:  # Most likely a Linux/Unix system anyway

                confighome =  os.path.join(os.path.expanduser('~'),'.config')

        configdir = os.path.join(confighome,app_name)

        return configdir
