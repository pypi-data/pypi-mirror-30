from setuptools import setup, find_packages

setup(
    name='aiorm',
    version='0.0.1',
    description='A simple orm for asyncio.',
    url='http://github.com/jeremaihloo/aiorm',
    author='jeremaihloo',
    author_email='jeremaihloo1024@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    zip_safe=False,
    # entry_points={
    #     'console_scripts': ['nory=nory.hotting:main'],
    # }
    install_requires=[
        'aiomysql',
        'asyncio-contextmanager'
    ],
)
