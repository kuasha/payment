try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='payment',
    version='0.00.001.00',
    packages=['payment'],
    url='http://cosmosframework.com',
    license='MIT License',
    author='Maruf Maniruzzaman',
    author_email='marufm@cosmosframework.com',
    description='Payment gateway library',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7'
    ],

    install_requires=['requests', 'mock'],

    test_suite="test"
)
