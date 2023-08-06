from setuptools import setup

setup(
    name='pyjsona',    # This is the name of your PyPI-package.
    version='0.1',                          # Update the version number for new releases
    # The name of your scipt, and also the command you'll be using for calling it
    packages=['jsona'],
    python_requires='>=3.6',
    author='Ryan Bonham',
    author_email='ryan@transparent-tech.com',
    license='MIT',
    description='Package for flattening JSON API 1.0 responses into easy to use dict & list.',
    url='https://github.com/TransparentTechnologies/pyJSONA'
)
