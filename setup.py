# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name='comment_style',
    version='0.1.1',
    description='An opinionated comment style checker.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Sean Kelleher',
    author_email='ezanmoto@gmail.com',
    python_requires='>=3.5.0',
    url='https://github.com/eZanmoto/comment_style',
    py_modules=['comment_style'],
    entry_points={
        'console_scripts': ['comment_style=comment_style:main'],
    },
    install_requires=[
        'pyyaml==5.3.1',
    ],
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
    ],
)
