import os

from setuptools import setup, find_packages

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
__VERSION__ = '0.1.1a'

base_requires = [
    "Django==1.11",
    "django-model-utils==3.0",
    "jsonfield==2.0.2",
    "celery==4.1.0",
    "django-environ==0.4.3",
    "redis==2.10.5",
    "boto3==1.4.6",
    "django-storages==1.6.5",
]

tests_requires = [
    "pytest==3.2.3",
    "flake8==3.5.0",
    "pytest-flake8==0.9.1",
    "pytest-cov==2.4.0",
    "pytest-django==3.1.2",
    "pytest-pythonpath==0.7.1",
    "pytest-xdist==1.20.0",
    "pytest-repeat==0.4.1",
    "django-autofixture==0.12.1",
    "django_extensions==1.7.9",
    "ipdb==0.10.3",
    "pyhamcrest==1.9",
]

setup(
    name="django-dde",
    version=__VERSION__,
    author="Stored",
    author_email="dev@stored.com.br",
    url="https://github.com/stored/django-dde",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description='Asynchronous and Distributed Data Exporter from a Django QuerySet',
    long_description=open(os.path.join(ROOT, 'README.md'), 'r', encoding='utf8').read(),
    install_requires=base_requires,
    setup_requires=base_requires,
    extras_require={
        'tests': tests_requires,
    },
    zip_safe=True,
    include_package_data=True,
)
