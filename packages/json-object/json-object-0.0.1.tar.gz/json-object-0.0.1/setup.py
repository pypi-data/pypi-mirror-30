from setuptools import setup, find_packages

setup(
    name='json-object',
    version='0.0.1',
    url='https://github.com/fdexfinancing/json-object',
    download_url='https://github.com/fdexfinancing/json-object/tarball/0.0.1',
    author='F(x)',
    author_email='ti@fdex.com.br',
    description='F(x) Json Object Package',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    license='MIT'
)