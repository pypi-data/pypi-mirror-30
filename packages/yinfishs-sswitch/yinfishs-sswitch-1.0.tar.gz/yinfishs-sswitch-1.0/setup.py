from setuptools import setup

setup(
    name='yinfishs-sswitch',            # This is the name of your PyPI-package.
    description='sswitch is a tool for managing .ssh configs.',
    license='GPL',
    version='1.0',                          # Update the version number for new releases
    scripts=['sswitch'],                  # The name of your scipt, and also the command you'll be using for calling it
    url='https://github.com/yinfish/sswitch.git'
)
