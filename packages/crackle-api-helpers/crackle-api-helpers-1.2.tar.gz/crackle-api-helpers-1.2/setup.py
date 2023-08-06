''' Setup for package '''
from setuptools import setup, find_packages

setup(
    name='crackle-api-helpers',
    version='1.2',
    description="crackle api helpers",
    long_description=""" """,
    classifiers=[],
    keywords='',
    author='Clark Mckenzie',
    author_email='clarkmckenzie@googlemail.com',
    url='https://github.com/cmck/crackle_api_helpers',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "requests",
        "urllib3"
    ],
)
