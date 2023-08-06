from distutils.core import setup

setup(
    name='CloeePy-Mongoengine',
    version='0.0.0-rc1',
    packages=['cloeepy_mongoengine',],
    package_data = {
        'cloeepy_mongoengine': ['data/*.yml'],
    },
    license='MIT',
    description="Mongoengine Plugin for CloeePy Framework",
    long_description=open('README.md').read(),
    install_requires=[
        "mongoengine>=0.10,<1",
        "CloeePy>=0",
     ],
     url = "https://github.com/cloeeai/CloeePy-Mongoengine",
     author = "Scott Crespo",
     author_email = "sccrespo@gmail.com",
     keywords = "mini framework cloee cloeepy mongo mongodb mongoengine",
     python_requires='~=3.3',
)
