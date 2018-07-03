import setuptools

setuptools.setup(
    name='pyksp',
    version='0.1',
    description='Library for building KSP code from Python classes',
    url='http://github.com/storborg/funniest',
    author='Levitanus',
    author_email='pianoist@ya.ru',
    license='GPLv3',
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'nose',
        'mypy',
        'pyqt5'
    ],
    zip_safe=False)
