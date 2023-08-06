from setuptools import setup

from ripiu.cmsplugin_fup import __version__

setup(
    name='ripiu.cmsplugin_fup',
    version=__version__,
    url='https://github.com/ripiu/cmsplugin_fup',
    license='BSD-new',
    description='Fast Undetermined Presentation',
    long_description=open('README.rst').read(),
    author='matteo vezzola',
    author_email='matteo@studioripiu.it',
    # find_packages doesn't like implicit namespace packages:
    # https://stackoverflow.com/questions/27047443/
    # packages=find_packages(),
    packages=['ripiu.cmsplugin_fup'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    # TODO: check requirements
    install_requires=[
        'Django >= 1.8',
        'django-cms >= 3.1',
        'django-colorfield>=0.1.14,<0.2.0',
    ],
    # ripiu is an implicit namespace package, so I need python>=3.3
    python_requires='>=3.3',
    include_package_data=True,
    zip_safe=False,
)
