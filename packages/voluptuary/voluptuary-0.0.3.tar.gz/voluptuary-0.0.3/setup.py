import setuptools

long_description = open('README.rst').read()

setup_params = dict(
    name='voluptuary',
    version='0.0.3',
    license='MIT',
    author='Paul Glass',
    author_email='pnglass@gmail.com',
    url='https://github.com/pglass/voluptuary',
    keywords='convert schema json voluptuous',
    packages=['voluptuary'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    description='convert json schemas to voluptuous schemas',
    long_description=long_description,
    install_requires=[
        'voluptuous',
        'jsonschema',
    ],
    entry_points={
        'console_scripts': [
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

if __name__ == '__main__':
    setuptools.setup(**setup_params)
