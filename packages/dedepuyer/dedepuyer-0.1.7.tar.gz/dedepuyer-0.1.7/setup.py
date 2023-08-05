from setuptools import setup

setup(
    name="dedepuyer",
    version='0.1.7',
    description="A project to find git information.",
    long_description="A project to find git information about authors' commits,most active days and time.",
    author="AdhiTj",
    author_email="adhitjatur@gmail.com",
    url="http://gitlab.h-seo.com/adhitj/dedepuyer",
    license="GPLv3+",
    py_modules=['dedepuyer'],
    entry_points='''
        [console_scripts]
        dedepuyer=dedepuyer:main
    ''',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2.7'
    )
)
