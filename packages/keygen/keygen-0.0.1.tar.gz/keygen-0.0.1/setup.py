from setuptools import setup, find_packages

from keygen import __version__

setup(
    name='keygen',
    version=__version__,
    url='',
    license='Freeware',
    author='Bobsans',
    author_email='mr.bobsans@gmail.com',
    maintainer='Bobsans',
    maintainer_email='mr.bobsans@gmail.com',
    description='Keygen for generate keys :)',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: Freeware',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ],
    keywords='key keygen secure',
    platforms=['Any'],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['keygen=keygen.keygen:main']
    }
)
