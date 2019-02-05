import setuptools  # type: ignore

setuptools.setup(
    name='pyksp',
    version='0.0.8',
    description='Library for building KSP code from Python classes',
    url='https://github.com/Levitanus/pyksp',
    author='Levitanus',
    author_email='pianoist@ya.ru',
    license='GPLv3',
    package_data={
        'pyksp': ['py.typed'],
    },
    packages=['pyksp'],
    install_requires=['pyperclip'],
    zip_safe=False)
