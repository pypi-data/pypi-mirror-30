from distutils.core import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='euring_code',
    version='0.1',
    description='Python support for EURING2000 and EURING2000+ codes',
    long_description=readme(),
    author='Dylan Verheul',
    author_email='dylan@dyve.net',
    keywords=['euring', ],  # arbitrary keywords
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    # url='https://github.com/euring/euring_code/',
    license='BSD-3-Clause-Clear',
    packages=['euring_code'],
    install_requires=[
        'chardet',
    ],
    zip_safe=False,
)
