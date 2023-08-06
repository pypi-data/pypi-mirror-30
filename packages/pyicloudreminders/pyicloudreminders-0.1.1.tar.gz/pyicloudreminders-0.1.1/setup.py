from setuptools import setup, find_packages


with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='pyicloudreminders',
    version='0.1.1',
    url='https://github.com/coumbole/pyicloudreminders',
    description=(
        'PyiCloudReminders is a module (a fork of pyicloud) which'
        'allows pythonistas to interact with iCloud Reminders.'
    ),
    maintainer='The PyiCloud + PyiCloudReminders Authors',
    maintainer_email='ville@kumpulainen.org',
    license='MIT',
    packages=find_packages(),
    install_requires=required,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'console_scripts': [
            'icloud = pyicloud.cmdline:main'
        ]
    },
)
