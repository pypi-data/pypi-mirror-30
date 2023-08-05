from setuptools import setup

setup(name = 'wordpress-cd-rancher',
    version = '0.1.0',
    description = 'Wordpress CD driver to deploy sites to Rancher environments.',
    author = 'Ross Golder',
    author_email = 'ross@golder.org',
    url = 'https://github.com/rossigee/wordpress-cd-rancher',
    install_requires = [
      'wordpress-cd'
    ],
    packages = [
      'wordpress_cd_rancher',
    ]
)
