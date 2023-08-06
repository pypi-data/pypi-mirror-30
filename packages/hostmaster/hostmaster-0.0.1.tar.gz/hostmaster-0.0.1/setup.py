from setuptools import setup, find_packages

from hostmaster import __version__

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='hostmaster',
    version=__version__,
    description='A simple way to master hosts',
    author='Yehuda Deutsch',
    author_email='yeh@uda.co.il',

    license='MIT',
    url='https://gitlab.com/uda/hostmaster',
    keywords='twisted hostmaster',
    packages=find_packages(),
    long_description=long_description,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Twisted',
        'Framework :: Zope',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
