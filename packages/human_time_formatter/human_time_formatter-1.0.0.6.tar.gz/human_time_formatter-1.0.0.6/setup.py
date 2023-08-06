from distutils.core import setup

# Read the version number
with open("human_time_formatter/_version.py") as f:
    exec(f.read())

setup(
    name='human_time_formatter',
    version=__version__, # use the same version that's in _version.py
    author='David N. Mashburn',
    author_email='david.n.mashburn@gmail.com',
    packages=['human_time_formatter'],
    scripts=[],
    url='http://pypi.python.org/pypi/human_time_formatter/',
    license='LICENSE.txt',
    description='Human-readable time delta formatter with relative precision ("ndigits")',
    long_description=open('README.txt').read(),
    install_requires=[
                      
                     ],
)
