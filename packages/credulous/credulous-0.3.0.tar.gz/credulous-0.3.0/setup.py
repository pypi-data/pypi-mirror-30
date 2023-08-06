from setuptools import setup

setup(
    name = 'credulous',
    packages = [
        'credulous'
    ],
    version = '0.3.0',
    description = 'Tool for generating API credentials',
    author = 'David O\'Connor',
    author_email = 'david.o@brainlabsdigital.com',
    url = 'https://github.com/davido-brainlabs/pycredulous',
    install_requires = [
        'google-auth-oauthlib'
    ],
    entry_points = {
        'console_scripts': [
            'credulous = credulous.__main__:main'
        ]
    }
)
