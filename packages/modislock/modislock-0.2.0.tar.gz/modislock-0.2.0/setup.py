"""
Modis Lock
-----

Modis Lock Description Here

````````````
Code Example:
.. code:: python
    from modis_admin_app import create_app

    app = create_app()

    if __name__ == "__main__":
        app.run()

`````````````````
And run it:
.. code:: bash
    $ pip install Flask
    $ python hello.py
    * Running on http://localhost:5000/
Ready for production? `Read this first <http://flask.pocoo.org/docs/deploying/>`.
Links
`````
* `website <http://flask.pocoo.org/>`_
* `documentation <http://flask.pocoo.org/docs/>`_
* `development version
  <https://github.com/pallets/flask/zipball/master#egg=Flask-dev>`_
"""

# Setuptools
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

# Subprocessing
from subprocess import run, CalledProcessError, TimeoutExpired

# Libraries
try:
    from distutils.sysconfig import get_python_lib as get_python_path
except ImportError:
    from site import getsitepackages as get_python_path

# Misc
from shutil import chown
import os
import sys
from pathlib import Path


if sys.version_info < (3, 5):
    raise Exception("Modis Lock requires Python 3.5 or higher.")

with open('./README.rst', encoding='utf-8') as f:
    readme = f.read()

requires = [i.strip() for i in open("./requirements.txt").readlines()]
mode = os.environ.get('MODE')


class PostDevelopCommand(develop):
    """Develop command for setuptools

    """
    def run(self):
        # TODO Post install script here or call a function
        develop.run(self)


class PostInstallCommand(install):
    """Install command for setuptools

    """
    install_dir = None
    hostname = None

    def _build_assets(self):
        """Builds the assets from static css and js files.

        :return:
        """
        if os.path.isdir(self.install_dir):
            os.chdir(self.install_dir)
            from modislock_webservice.extensions import asset_bundles
            from webassets.exceptions import BundleError
            from webassets import Environment

            os.chdir(self.install_dir)
            env = Environment(directory=self.install_dir + '/static', url='/static')

            for key in asset_bundles.keys():
                try:
                    env.register(key, asset_bundles[key])
                    env[key].urls()
                except BundleError as e:
                    print(f'Bundle Error: {e}')
                    continue

    def _build_documentation(self):
        print(f'Documentation generation complete in directory: {self.install_dir}')

    def _gen_keys(self):
        key_args = ['openssl', 'genrsa', '-out', '/var/www/modislock.key', '2048']
        cert_args = ['openssl', 'req', '-new', '-x509', '-key', '/var/www/modislock.key', '-out',
                     '/var/www/modislock.cert',
                     '-days', '3650', '-subj']

        try:
            # Generate the key
            run(key_args, timeout=30)
        except (CalledProcessError, TimeoutExpired):
            print('Error generating key')
        except Exception as e:
            print(f'OS Error: {e}')

        # Generate certificate
        cert_args.append('/CN=' + self.hostname + '.local')

        try:
            run(cert_args, timeout=30)
        except (CalledProcessError, TimeoutExpired):
            print('Error generating certificate')
        except Exception as e:
            print(f'OS Error: {e}')

    def _pre_install(self):
        # Install OS dependencies
        try:
            pre_args = ['apt', 'install', '-y', 'libsystemd-dev', 'libffi-dev', 'libssl-dev']
            run(pre_args, timeout=60)
        except (CalledProcessError, TimeoutExpired):
            print('Error installing dependencies')
        except Exception as e:
            print(f'OS Error: {e}')

    def _post_install(self):
        # Create a symbolic link for the web server to find the static files
        # Check for existing link
        web_path = '/var/www/modislock'
        site_src_path = '/etc/nginx/sites-available'
        site_dst_path = '/etc/nginx/sites-enabled'
        demo_site = os.path.join(site_dst_path, 'admin_site_demo')
        admin_site = os.path.join(site_dst_path, 'admin_site')

        # Delete all symlinks
        if Path(web_path).is_symlink():
            Path(web_path).unlink()
        if Path(demo_site).is_symlink():
            Path(demo_site).unlink()
        if Path(admin_site).is_symlink():
            Path(admin_site).unlink()

        # Create link from install directory to /var/www/modislock
        try:
            Path(web_path).symlink_to(self.install_dir, target_is_directory=True)
        except Exception as e:
            print(f'Error: {e}')
        # Create link for all nginx files to enabled
        try:
            Path(os.path.join(site_src_path, 'admin_site_demo' if mode == 'DEMO' else 'admin_site'))\
                .symlink_to(os.path.join(site_dst_path, 'admin_site_demo' if mode == 'DEMO' else 'admin_site'))
        except Exception as e:
            print(f'Error: {e}')

        if mode != 'DEMO':
            self._gen_keys()
            print('Generation of keys completed')

        self._build_assets()
        print('Building assets completed')
        self._build_documentation()
        print('Building documentation completed')

        # Permissions
        for r, d, f in os.walk(self.install_dir + '/pages'):
            try:
                chown(r, user='root', group='www-data')
                os.chmod(r, 0o755)
            except LookupError as e:
                print(f'Permission errors: {e}')

        for r, d, f in os.walk(self.install_dir + '/static'):
            try:
                chown(r, user='root', group='www-data')
                os.chmod(r, 0o755)
            except LookupError as e:
                print(f'Permission errors: {e}')

        print('Calling restart of processes')

        try:
            args = ['systemctl', 'restart', 'nginx']
            run(args, timeout=20)
        except (CalledProcessError, TimeoutExpired):
            print('Restart of processes failed')
        except Exception as e:
            print(f'OS Error: {e}')

        try:
            args = ['supervisorctl', 'reload']
            run(args, timeout=20)
        except (CalledProcessError, TimeoutExpired):
            print('Error reloading supervisor')
        except Exception as e:
            print(f'OS Error: {e}')
        else:
            args = ['supervisorctl', 'restart', 'admin:*']

            try:
                run(args, timeout=45)
            except (CalledProcessError, TimeoutExpired):
                print('Error restarting web admin')
            except Exception as e:
                print(f'OS Error: {e}')

    def run(self):
        # Generate the certificate
        with open('/etc/hostname', 'r') as f:
            self.hostname = f.readline().rstrip()

        # self.install_dir = site.getsitepackages()[0] + '/modislock_webservice'
        self.install_dir = get_python_path() + '/modislock_webservice'
        print('Installation directory: ' + self.install_dir)

        if not os.path.exists(self.install_dir):
            os.mkdir(self.install_dir, mode=0o755)

        # Pre-install
        self._pre_install()
        print('Pre-install completed')
        # Install
        try:
            install.run(self)
        except:
            print('Error occurred in installation')
        # Post-install
        print('Post-install beginning')
        self._post_install()
        print('Post-install completed')


setup(
    name='modislock',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.2.0',

    description='Administration web interface for Modis© Lock',
    long_description=readme,

    # The project's main homepage.
    url='https://github.com/Modis-GmbH/ModisLock-WebAdmin',

    # Choose your license
    license='GPL',

    # Author details
    author='Richard Lowe',
    author_email='richard@modis.io',

    # What does your project relate to?
    keywords=['modis', 'raspberry pi', 'lock', 'administration'],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Environment :: Console",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security"
    ],

    platforms=['Linux', 'Raspberry Pi'],

    zip_safe=False,

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=requires,

    # If your project only runs on certain Python versions, setting the python_requires argument to the appropriate
    # PEP 440 version specifier string will prevent pip from installing the project on other Python versions.
    python_requires='>=3.5',

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    data_files=[('/etc/supervisor/conf.d', ['deploy/modis_admin.conf']),
                ('/etc/nginx/sites-available', ['deploy/admin_site']),
                ('/etc/nginx/sites-available', ['deploy/supervisord_site']),
                ('/etc/nginx/sites-available', ['deploy/admin_site_demo'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'modis_admin = modislock_webservice.wsgi:main',
            'modis_admin_worker = modislock_webservice.celery_worker:main'
        ]
    },

    cmdclass={'develop': PostDevelopCommand,
              'install': PostInstallCommand}
)
