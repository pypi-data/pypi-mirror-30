from setuptools import setup
from setuptools.command.install import install
import os



class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        usr = os.path.expanduser("~")
        if not os.path.isdir(os.path.join(usr, 'iptv4plex')):
            os.mkdir(os.path.join(usr, 'iptv4plex'))
        with open(os.path.join(usr, 'iptv4plex', 'iptv4plex.py'), "wb") as file:
            # get request
            from requests import get
            response = get("https://raw.githubusercontent.com/vorghahn/iptv4plex/master/iptv4plex.py")
            # write to file
            file.write(response.content)


setup(
  name = 'iptv4plex',
  version = '1.0',
  cmdclass = {'install': PostInstallCommand},
  description = 'm3u8 proxy 4 plex',
  python_requires = '>=3.5',
  install_requires=[
          'requests',
          'flask'
  ]
)