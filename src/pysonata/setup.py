from setuptools import setup, find_packages
import sonata


package_name = 'sonata'
package_version = sonata.__version__


def prepend_find_packages(*roots):
    """Recursively traverse nested packages under the root directories"""
    packages = []
    for root in roots:
        packages += [root]
        packages += [root + '.' + s for s in find_packages(root)]

    return packages


with open('README.md', 'r') as fhandle:
    long_description = fhandle.read()


setup(
    name='sonata',
    version='0.0.1',
    description='SONATA Data Format',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AllenInstitute/bmtk',
    package_data={'': ['*.md', '*.txt', '*.cfg', '**/*.json', '**/*.hoc']},
    tests_require=['pytest'],
    install_requires=[
        'jsonschema',
        'pandas',
        'numpy',
        'six',
        'h5py'
    ],
    packages=prepend_find_packages(package_name),
    include_package_data=True,
    platforms='any',
    keywords=['neuroscience', 'scientific', 'modeling', 'networks', 'simulation'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ]
)