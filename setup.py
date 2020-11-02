from setuptools import find_packages, setup


def read_file(name):
    with open(name, 'r') as f:
        content = f.read().rstrip('\n')
    return content


setup(
    name='connect-openapi-client',
    author='CloudBlue',
    url='https://connect.cloudblue.com',
    description='Connect Python OpenAPI Client',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    zip_safe=True,
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_file('requirements/prod.txt').splitlines(),
    setup_requires=['setuptools_scm', 'pytest-runner', 'wheel'],
    use_scm_version=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='fulfillment api client openapi utility connect cloudblue',
)
