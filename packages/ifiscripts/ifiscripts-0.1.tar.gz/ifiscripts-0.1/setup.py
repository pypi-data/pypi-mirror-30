from setuptools import setup
setup(
    author='Kieran O\'Leary',
    author_email='kieran.o.leary@gmail.com',
    description='IFIscripts',
    scripts=['sipcreator.py', 'ififuncs.py', 'copyit.py'],
    entry_points={
        'console_scripts': [
            'copyit.py=copyit:main',
        ],
    },
    license='MIT',
    name='ifiscripts',
    version='0.01'
)
