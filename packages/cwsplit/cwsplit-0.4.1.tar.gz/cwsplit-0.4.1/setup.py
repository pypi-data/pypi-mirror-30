from distutils.core import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='cwsplit',
    version='0.4.1',
    description="Compund word splitter for enchant supported languages",
    long_description=read('README'),
    author='Ivan Nesic',
    author_email='contact@droll.science',
    url='http://droll.science',
    python_requires='>=3',
    packages=['cwsplit'],
    install_requires=['pyenchant'],
    license='MIT',
    keywords='compound word splitter language english german',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ]
)
