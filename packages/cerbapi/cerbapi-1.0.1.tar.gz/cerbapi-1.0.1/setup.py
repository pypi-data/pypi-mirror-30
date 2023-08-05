from distutils.core import setup
from cerbapi import __version__

setup(
    name='cerbapi',
    version=__version__,
    packages=['cerbapi'],
    url='https://github.com/CyberTechCafe-LLC/cerbapi',
    license='GNU General Public License v3.0',
    author='Rob Adkerson',
    author_email='r.j.adkerson@gmail.com',
    description='Python package for the Cerb.ai API',
    keywords=['cerb', 'cerb.ai', 'api']
)