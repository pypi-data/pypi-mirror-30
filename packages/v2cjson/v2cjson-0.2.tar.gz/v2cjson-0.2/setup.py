from setuptools import setup

setup(
    name='v2cjson',
    version='0.2',
    description='Var 2 cool highlighted JSON',
    url='https://github.com/57uff3r/pearsondictionary',
    packages=['v2cjson'],
    zip_safe=False,
    license='MIT',
    author='Andrey Korchak',
    author_email='57uff3r@gmail.com',
    install_requires=[
        'Pygments==2.2.0',
    ],
)