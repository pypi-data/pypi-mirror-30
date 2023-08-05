from setuptools import setup

with open('README.rst', 'r') as file_object:
    readme = file_object.read()

setup(
    name = 'envassume',
    version = '1.0.2',
    description = 'Assume an AWS IAM role from AWS API credentials in environment variables',
    long_description = readme,
    license = 'MIT',
    author = 'Warren Moore',
    author_email = 'warren@wamonite.com',
    url = 'https://github.com/wamonite/envassume',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ],
    packages = ['envassume'],
    entry_points = dict(console_scripts = ['envassume=envassume.main:run']),
    install_requires = [
        'boto3==1.6.16',
        'attrs==17.4.0'
    ],
    zip_safe = False
)
