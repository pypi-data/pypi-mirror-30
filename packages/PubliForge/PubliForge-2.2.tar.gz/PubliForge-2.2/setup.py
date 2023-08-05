"""Setup for PubliForge."""

import os
from setuptools import setup, find_packages, Extension

VERSION = '2.2'

REQUIRES = [
    'future',
    'configparser',
    'pyramid >= 1.6',
    'pyramid_beaker >= 0.8',
    'pyramid_rpc >= 0.7',
    'pyramid_chameleon >= 0.3',
    'WebHelpers2 >= 2.0',
    'colander >= 1.0',
    'SQLAlchemy >= 1.0',
    'psycopg2 >= 2.6',
    'lxml >= 3.5',
    'pycrypto >= 2.6',
    'Mercurial >= 3.6, < 3.8',
    'hgsubversion >= 1.8',
    'subvertpy >= 0.9',
    'docutils >= 0.12',
    'Pygments >= 2.0',
    'Whoosh >= 2.7',
    'pillow >= 4.0',
    'piexif >= 1.0',
    'waitress >= 0.8',
    'WebError >= 0.11',
]

TESTS_REQUIRE = [
    'WebTest >= 2.0',
    'nose',
]

DOCUMENTATION_REQUIRE = [
    'Sphinx',
    'sphinx_paramlinks',
]

DEVELOPMENT_REQUIRE = TESTS_REQUIRE + DOCUMENTATION_REQUIRE + [
    'pylint',
    'flake8',
    'Babel',
    'pyramid_debugtoolbar',
]

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.txt')) as hdl:
    README = hdl.read()
with open(os.path.join(HERE, 'CHANGES.txt')) as hdl:
    CHANGES = hdl.read()

setup(
    name='PubliForge',
    version=VERSION,
    description='Online multimedia publishing system',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Patrick PIERRE',
    author_email='patrick.pierre@lap2.fr',
    url='http://docs.publiforge.org',
    keywords='web wsgi bfg pylons pyramid publiforge',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='publiforge',
    install_requires=REQUIRES,
    extras_require={
        'testing': TESTS_REQUIRE,
        'documentation': DOCUMENTATION_REQUIRE,
        'development': DEVELOPMENT_REQUIRE,
    },
    ext_modules=[Extension(
        'publiforge.lib.rsync._librsync',
        ['publiforge/lib/rsync/_librsync.c'],
        libraries=['rsync'])],
    message_extractors={'publiforge': [
        ('**.py', 'python', None),
        ('**.pt', 'mako', {'input_encoding': 'utf-8'}),
    ]},
    entry_points="""\
    [paste.app_factory]
    main = publiforge:main

    [console_scripts]
    pfpopulate = publiforge.scripts.pfpopulate:main
    pfbackup = publiforge.scripts.pfbackup:main
    pfbuild = publiforge.scripts.pfbuild:main
    pftexmath = publiforge.scripts.pftexmath:main
    pfimage2svg = publiforge.scripts.pfimage2svg:main
    pfminify = publiforge.scripts.pfminify:main
    pfscheduler = publiforge.scripts.pfscheduler:main

    [pyramid.scaffold]
    publiforge_front=publiforge.scaffolds:PubliForgeFrontScaffold
    publiforge_leprisme=publiforge.scaffolds:PubliForgeLePrismeScaffold
    """,
)
