from setuptools import setup

long_description = open('README.md', 'r').read()
setup(
    name='lbdict',
    description='A class for storing the pixel values of letters.',
    long_description=long_description,
    version='0.1.1',
    url='https://github.com/Jugbot/Letter-Bitmap-Dictionary',
    keywords='bitmap font dictionary',
    author='Jugbot',
    author_email='lucasp465@gmail.com',
    install_requires=['pillow'],
    py_modules=['lbdict']
)