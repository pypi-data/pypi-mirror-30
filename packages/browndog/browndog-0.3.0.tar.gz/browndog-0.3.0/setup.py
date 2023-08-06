from setuptools import setup

setup(
    name='browndog',
    packages=['browndog'],
    version='0.3.0',
    description='''Brown Dog Python library''',
    long_description='This Python library wraps the Brown Dog REST API endpoints. It provides methods to interact with '
                     'Brown Dog services and perform actions such as conversion of files to desirable formats, '
                     'extraction of metadata from files, and indexing and querying of collections of files. For more '
                     'information about Brown Dog and its services, please visit https://browndog.ncsa.illinois.edu/.',
    author='Kenton McHenry',
    author_email='browndog-support@ncsa.illinois.edu',
    url='https://browndog.ncsa.illinois.edu/',
    download_url='https://opensource.ncsa.illinois.edu/bitbucket/projects/BD/repos/bd.py',
    keywords=['Brown Dog', 'Unstructured Data Curation', 'Big Data Processing', 'Long Tail'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=['requests==2.11.1', 'docker-py==1.10.6', 'numpy==1.12.0', 'python-docker-machine==0.2.2'],
    zip_safe=False
)
