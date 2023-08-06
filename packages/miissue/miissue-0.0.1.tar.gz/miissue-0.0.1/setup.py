from setuptools import setup

setup(
    name='miissue',
    version='0.0.1',
    py_modules=['miissue'],
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        miissue=miissue:cli
    ''',
	url='https://github.com/claymodel/miissue',
	author='Elias Hasnat',
	author_email='android.hasnat@gmail.com',
)
