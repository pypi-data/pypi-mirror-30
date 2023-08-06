from setuptools import setup

setup(
    name='service-container',
    version='0.1.0',
    packages=['servicecontainer'],
    license='MIT',
    author='Heureka.cz',
    author_email='vyvoj@heureka.cz',
    description='Dependency injection container with parameters and transaction control.',
    url='https://github.com/heureka/service-container',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='dependency injection container ioc di',
    python_requires='>=3',
)
