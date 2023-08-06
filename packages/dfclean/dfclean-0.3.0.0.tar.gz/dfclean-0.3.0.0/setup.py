from distutils.core import setup

setup(
    name='dfclean',
    version='0.3.0.0',
    packages=['dfcleanlib'],
    url='https://gitlab.com/panter_dsd/distfilescleaner',
    license='GPLv3',
    author='PanteR',
    author_email='panter.dsd@gmail.com',
    description='Clean up old distfiles in Gentoo',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    requires=['humanize'],
    scripts=['dfclean']
)
