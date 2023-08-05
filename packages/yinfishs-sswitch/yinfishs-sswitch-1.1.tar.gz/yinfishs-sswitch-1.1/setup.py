from setuptools import setup

setup(
    name='yinfishs-sswitch',            # This is the name of your PyPI-package.
    description='sswitch is a tool for managing .ssh configs.',
    license='GPL',
    version='1.1',                          # Update the version number for new releases
    entry_points={  # Optional
        'console_scripts': [
            'sswitch=sswitch:main',
        ],
    },
    url='https://github.com/yinfish/sswitch.git'
)
