import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


def import_version():
    from waves.wcore import __version_detail__
    return __version_detail__


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='waves-core',
    version=import_version(),
    packages=find_packages(),
    provides=['waves'],
    include_package_data=True,
    license='GPLv3',
    description='WAVES - core package',
    url='http://waves.atgc-montpellier.fr',
    author='Marc Chakiachvili',
    author_email='marc.chakiachvili@gmail.com',
    install_requires=[
        'coreapi==2.3.3',
        'Django<=1.11.11',
        'daemons==1.3.0',
        'django-cors-headers==2.2.0',
        'django-crispy-forms==1.7.2',
        'django-polymorphic==2.0.2',
        'djangorestframework==3.7.7',
        'inflection==0.3.1',
        'psutil==5.4.0',
        'pycrypto==2.6.1',
        'python-magic==0.4.13',
        'saga-python==0.47',
        'setproctitle==1.1.10',
        'six==1.11.0',
        'swapper==1.1.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: System :: Distributed Computing',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Operating System :: Unix'
    ],
)
