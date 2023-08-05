from setuptools import setup

setup(name = 'ga-library',
    version = '0.1',
    description = 'Generic library implementing standard genetic algorithm based methods.',
    url = 'http://github.com/gcappon/ga-library',
    author= 'Giacomo Cappon',
    author_email = 'cappongiacomo@gmail.com',
    license = 'GNU General Public License v3 (GPLv3)',
    packages = ['ga-library'],
    classifiers = ['Development Status :: 1 - Planning',
                'Intended Audience :: Developers',
                'Topic :: Software Development :: Build Tools',
                'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                'Programming Language :: Python :: 3.6',
                ],
    install_requires=[
        'numpy',
    ],
    zip_safe = False)