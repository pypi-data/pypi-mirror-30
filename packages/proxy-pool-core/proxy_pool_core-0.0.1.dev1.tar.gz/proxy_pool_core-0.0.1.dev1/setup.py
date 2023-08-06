from setuptools import find_packages, setup


setup(
    name='proxy_pool_core',
    version='0.0.1dev1',
    packages=find_packages(exclude=[]),
    include_package_data=True,
    zip_safe=False,

    description='A Proxy Pool Project.',
    long_description='TODO',

    author='Sean Xu',
    author_email='xuqingjian8@gmail.com',

    keywords='proxy proxypool validate tornado',

    install_requires=[
        "tornado",
    ]
)
