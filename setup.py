import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='beets-websearch',
    version='0.0.0-dev',
    author='Max Goltzsche',
    description='Search tracks and generate playlists',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mgoltzsche/beets-websearch',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'beets',
        'fastapi',
    ]
)
