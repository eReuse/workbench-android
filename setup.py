from setuptools import find_packages, setup


def requires(extra=''):
    with open('requirements{}.txt'.format(
            '-' + extra if extra else '')) as fh:
        return fh.read().split()


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
    install_requires=requires(),
    setup_requires=requires('setup'),
    tests_require=requires('tests'),
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
    extras_require={
        'docs': requires('docs')
    },
)
