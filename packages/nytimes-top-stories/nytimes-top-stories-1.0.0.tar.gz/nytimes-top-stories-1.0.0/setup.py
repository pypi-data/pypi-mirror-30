from setuptools import setup

setup (

    name='nytimes-top-stories',
    version='1.0.0',
    description='Python wrapper for NYTimes Top Stories API',
    long_description=open('README.rst').read(),
    url='http://github.com/kaarora123/nytimes-top-stories',
    author='Kashish Arora',
    author_email='kashisharora99@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='new york times nytimes top stories api',
    packages=['topstories'],
    install_requires=[
        'requests >= 2.1.0',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'mock']
)
