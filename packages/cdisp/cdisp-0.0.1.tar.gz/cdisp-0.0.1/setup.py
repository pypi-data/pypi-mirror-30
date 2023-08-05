import os
import sys
import codecs

from setuptools import setup


version = '0.0.1'

HERE = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    readme = f.read()


setup_requires = ['pytest-runner'] if \
    {'pytest', 'test', 'ptr'}.intersection(sys.argv) else []

setup(
    name='cdisp',
    version=version,
    author='Felippe Barbosa',
    author_email='felippe.barbosa@gmail.com',
    license='MIT v1.0',
    url='https://github.com/fbarbosa/cdisp',
    description='My personal support packages for dispersion and nonlinear optics analysis using COMSOL simulations',
    long_description=readme,
    keywords='dispersion COMSOL',
    packages=['cdisp'],
    package_dir={'cdisp': 'cdisp'},
    ext_modules=[],
    provides=['cdisp'],
    install_requires=['numpy', 'scipy', 'pandas'] + (['future']
                                  if sys.version_info.major < 3 else []),
    setup_requires=setup_requires,
    tests_require=[],
    platforms='OS Independent',
    classifiers=[
        'Topic :: Scientific/Engineering :: Physics',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)'
    ],
    zip_safe = False,
    include_package_data = True)
