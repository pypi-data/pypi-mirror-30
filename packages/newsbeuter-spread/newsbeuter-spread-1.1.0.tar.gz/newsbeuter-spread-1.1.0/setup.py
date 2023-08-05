from setuptools import setup, find_packages
from newsbeuter_spread import __version__ as version


setup(
    name="newsbeuter-spread",
    version=version,
    description=('Web frontend for newsbeuter db'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='newsbeuter newsbeuter-spread',
    author='Jon Robison',
    author_email='narfman0@gmail.com',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=['flask', ],
    test_suite='tests/test_newsbeuter_spread',
)
