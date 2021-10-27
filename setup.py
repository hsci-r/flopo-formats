from setuptools import setup, find_packages

with open('README.md') as fp:
    README = fp.read()

setup(
    name='flopo-formats',
    version='0.1.0',
    author='Maciej Janicki',
    author_email='maciej.janicki@helsinki.fi',
    description='Tools for converting between data formats used in the FloPo project.',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages('src', exclude=['tests', 'tests.*']),
    package_dir={'': 'src'},
    test_suite='tests',
    install_requires=[],
    entry_points={
        'console_scripts' : [
            'flopo-convert   = flopo_formats.scripts.convert:main',
            'flopo-finer     = flopo_formats.scripts.finer:main',
            'flopo-export    = flopo_formats.scripts.export:main',
            'flopo-eval      = flopo_formats.scripts.eval:main',
            'flopo-package   = flopo_formats.scripts.package:main',
            'flopo-csv-merge-articles   = flopo_formats.scripts.csv_merge_articles:main',
        ]
    }
)
