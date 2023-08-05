from setuptools import setup

VERSION = '0.0.4'

if __name__ == '__main__':
    setup(
        name='lomp',
        packages=['lomp'],
        version=VERSION,
        description='Memory-efficient parallelism',
        author='Jim Rybarski',
        author_email='jim@rybarski.com',
        url='https://github.com/jimrybarski/lowmem-parallel',
        download_url='https://github.com/jimrybarski/lowmem-parallel/tarball/%s' % VERSION,
        keywords=['memory', 'parallel', 'parallelism'],
        classifiers=['Development Status :: 3 - Alpha',
                     'License :: Freely Distributable',
                     'License :: OSI Approved :: BSD License',
                     'Operating System :: POSIX :: Linux',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3.3',
                     'Programming Language :: Python :: 3.4',
                     'Programming Language :: Python :: 3.5',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     ]
    )
