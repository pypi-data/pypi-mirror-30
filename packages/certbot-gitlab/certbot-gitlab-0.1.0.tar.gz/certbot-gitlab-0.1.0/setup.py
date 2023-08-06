from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='certbot-gitlab',
    version='0.1.0',
    description='GitLab Pages plugin for Certbot',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/sommd/certbot-gitlab',
    author='sommd',
    license='Apache Licence 2.0',
    
    packages=find_packages(),
    
    install_requires=[
        'certbot',
        'zope.interface',
        'python-gitlab',
    ],
    
    entry_points={
        'certbot.plugins': [
            'gitlab = certbot_gitlab.configurator:GitLabConfigurator',
        ],
    },
)
