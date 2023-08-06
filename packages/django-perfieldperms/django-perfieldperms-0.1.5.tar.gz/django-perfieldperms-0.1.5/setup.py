import os
from setuptools import find_packages, setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__),
    os.pardir)))
    
setup(
        name='django-perfieldperms',
        version='0.1.5',
        packages=find_packages(exclude=['tests*']),
        include_package_data=True,
        license='Apache-2.0',
        description='Per model field permissions for Django.',
        url='https://gitlab.anu.edu.au/CIMS/django-perfieldperms',
        author='Lincoln Smith',
        author_email='lincoln.smith@anu.edu.au',
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3 :: Only',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Development Status :: 3 - Alpha',
            'Environment :: Web Environment',
            'Framework :: Django :: 1.11',
            'Intended Audience :: Developers',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        install_requires=['django>=1.11,<1.11.999'],
        python_requires='~=3.4',
        long_description="""\
Implements model field permissions for Django.

Provides models and an authentication/authorisation backend to enable permissions to be set at the
field level of a django model. Also provides Django admin and form classes to assist with
integration of field level permissions into the rest of Django.
""",
        )

