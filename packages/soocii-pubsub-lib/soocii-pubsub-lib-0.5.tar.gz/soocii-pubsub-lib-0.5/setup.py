# Sample https://github.com/pypa/sampleproject

from setuptools import setup, find_packages

setup(
    name='soocii-pubsub-lib',
    version='0.5',
    url='https://github.com/drmobile/pubsub-broker',
    license='Apache Software License',
    author='Soocii',
    author_email='service@soocii.me',
    description='Library for Soocii back-end services to integrate with Google Cloud Pub/Sub service.',
    packages=find_packages(exclude=['tests']),
    long_description=open('README.md').read(),
    zip_safe=False,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ]
)
