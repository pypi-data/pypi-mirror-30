from distutils.core import setup
#from Cython.Build import cythonize

setup(
    name='text-fabric',
    packages=['tf'],
    version='3.2.4',
    description='''Processor for Text Fabric Data''',
    author='Dirk Roorda',
    author_email='dirk.roorda@dans.knaw.nl',
    url='https://github.com/Dans-labs/text-fabric',
    keywords = ['text', 'linguistics', 'database', 'graph', 'hebrew', 'greek', 'syriac'],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Education",
        "Intended Audience :: Religion",
        "Intended Audience :: Science/Research",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Natural Language :: Hebrew",
        "Natural Language :: Greek",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Religion",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    long_description = '''\
Tools to read Text-Fabric resources analyse them efficiently.
More info on https://github.com/Dans-labs/text-fabric/wiki
''',
)
