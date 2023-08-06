from setuptools import setup

setup(
    name='aroundtheworlds',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: pygame',
        'Topic :: Games/Entertainment :: Arcade',
    ],
    # data_files=[('.', ['alembic.ini'])],
    license='LGPL',
    author='René dudfield',
    author_email='renesd@gmail.com',
    maintainer='Rene Dudfield',
    maintainer_email='renesd@gmail.com',
    description='Around the worlds in 80 days.',
    include_package_data=True,
    long_description='',
    package_dir={'aroundtheworlds': 'aroundtheworlds'},
    packages=['aroundtheworlds'],
    # package_data={'solarwolf': []},
    url='https://github.com/illume/aroundtheworlds',
    install_requires=['pygame'],
    version='0.0.1.dev1',
    entry_points={
        'console_scripts': [
            'aroundtheworlds=aroundtheworlds.aroundtheworlds:main',
        ],
    },
)