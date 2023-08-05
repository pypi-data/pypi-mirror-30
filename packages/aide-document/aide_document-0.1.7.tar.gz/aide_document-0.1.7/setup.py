from setuptools import setup, find_packages

setup(
    name='aide_document',
    version='0.1.7',
    description='Provides templating engine for use within the AguaClara AIDE.',
    url='https://github.com/AguaClara/aide_document',
    author='Cornell University AguaClara',
    author_email='aguaclara@cornell.edu',
    license = 'MIT',
    packages=find_packages(),
    install_requires=['jinja2'],
    include_package_data=True,
    test_suite="tests",
    zip_safe=False
)