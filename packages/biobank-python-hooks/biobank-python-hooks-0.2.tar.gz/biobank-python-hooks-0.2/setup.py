from setuptools import setup, find_packages

setup(
    name='biobank-python-hooks',
    description='Hooks to allow system to integrate with PHP Biobank server',
    url='https://bitbucket.org/lshtmweb/biobank-python-tools',
    author='LSHTM Web',
    author_email='webteam@lshtm.ac.uk',
    license='TBC',
    version='0.2',
    keywords='kobotoolbox ona cureme',
    install_requires=['Django>=1.4', 'requests', 'django-oauth-tokens', 'django-fieldsignals', 'djangorestframework',
                      'oauth2_provider'],
    packages=find_packages(),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Framework :: Django',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
