from setuptools import setup

VERSION = '1.1'

if __name__ == '__main__':
    setup(
        name='finkelsteinlabpalette',
        packages=['flabpal'],
        version=VERSION,
        description='Finkelstein Lab standard color palette',
        author='Jim Rybarski',
        author_email='jim@rybarski.com',
        url='https://github.com/jimrybarski/finkelstein-lab-palette',
        download_url='https://github.com/jimrybarski/finkelstein-lab-palette/tarball/%s' % VERSION,
        keywords=['color', 'palette', 'colorblind'],
        classifiers=['Development Status :: 4 - Beta',
                     'Intended Audience :: Science/Research',
                     'License :: Freely Distributable',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 3',
                     'Topic :: Scientific/Engineering :: Visualization',
                     'Natural Language :: English'
                     ]
    )
