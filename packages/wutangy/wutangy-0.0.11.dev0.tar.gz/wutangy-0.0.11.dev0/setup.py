from setuptools import setup, find_packages

try:
    with open('README.rst') as file:
        long_description = file.read()
except Exception as error:
    print("Could not find README.rst for long description. Error: {}".format(
        error))
    print("Leaving long_description as None")
    long_description = None

setup(
    name='wutangy',
    author='elias julian marko garcia',
    author_email='elias.jm.garcia@gmail.com',
    description=(
        'wutangy is a WuTang inspired lorem ispsum generator, SUUUUUUUUUU'),
    url='https://github.com/ejmg/wutangy',
    version='0.0.11dev',
    packages=find_packages(),
    entry_points={
        "console_scripts": ['wutangy = wutangy.wutangy:wu'],
    },
    install_requires=[],
    include_package_data=True,
    license='MIT',
    long_description=long_description)
