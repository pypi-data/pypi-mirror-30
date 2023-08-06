from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='interscratch',
    version='0.3.0',
    description='http extension to send messages between scratch projects',
    long_description=long_description,
    url='https://github.com/pypa/sampleproject',
    author='Vincent Guffens',
    author_email='vincent.guffens@gmail.com',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',

        # Pick your license as you wish
	'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    python_requires='>=2.7',
    keywords='scratch',
    packages=find_packages(exclude=['resources']),
    install_requires=['tornado'],
    extras_require={
    },
    package_data={
        'interscratch': ['resources/*'],
    },
    data_files=[],
    include_package_data = True,
    entry_points={
        'console_scripts': [
            'interscratchc=interscratch.interscratchc:main',
            'interscratchs=interscratch.interscratchs:main',
        ],
    },
    project_urls={
    },
)
