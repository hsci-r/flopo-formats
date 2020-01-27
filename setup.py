from setuptools import setup, find_packages

with open('README.md') as fp:
    README = fp.read()

setup(
    name='flopo_utils',
    version='0.1.0',
    author='Maciej Janicki',
    author_email='maciej.janicki@helsinki.fi',
    description='Various utilities to be used in the FLOPO project',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages('src', exclude=['tests', 'tests.*']),
    package_dir={'': 'src'},
    test_suite='tests',
    install_requires=[],
    entry_points={
        'console_scripts' : [
            'flopo-annotate  = flopo_utils.scripts.annotate:main',
            'flopo-convert   = flopo_utils.scripts.convert:main',
            'flopo-finer     = flopo_utils.scripts.finer:main',
            'flopo-export    = flopo_utils.scripts.export:main',
            'flopo-eval      = flopo_utils.scripts.eval:main',
            'flopo-package   = flopo_utils.scripts.package:main',
        ]
    }
)
