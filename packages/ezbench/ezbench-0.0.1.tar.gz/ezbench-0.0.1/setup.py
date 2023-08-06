from distutils.core import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='ezbench',
    packages=[
        'ezbench',
    ],
    package_dir={
        'ezbench': 'src',
    },
    version='0.0.1',
    license="Apache 2.0 license",
    description='Small and helpfull tool for benchmarking',
    long_description=readme,
    author='Eugene Ivanchenko',
    author_email='ez@eiva.info',
    url='https://github.com/eiva/ezbench',
    download_url='https://pypi.python.org/pypi/ezlog',
    keywords=['tool', 'performance', 'measure', 'benchmark'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English'],
)
