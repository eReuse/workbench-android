from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='workbench-android',
    version='0.1a1',
    packages=find_packages(),
    description='',
    url='https://github.com/ereuse/workbench-android',
    author='eReuse.org team',
    author_email='x.bustamante@ereuse.org',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'blessed',
        'colorama',
        'click >= 6.0',
        'ereuse-utils[cli, naming]>=0.4.0b20'
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Logging',
        'Topic :: Utilities',
    ],
    py_modules=['devicetag'],
    entry_points={
        'console_scripts': [
            'wa = workbench_android.main:main',
        ],
    },
)
