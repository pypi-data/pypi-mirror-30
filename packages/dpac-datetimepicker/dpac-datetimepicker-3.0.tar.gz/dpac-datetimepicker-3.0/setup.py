from setuptools import setup


setup(
    name='dpac-datetimepicker',
    packages=['bootstrap3_datetime',],
    package_data={'bootstrap3_datetime': ['static/bootstrap3_datetime/css/*.css', 
                                          'static/bootstrap3_datetime/js/*.js',
                                          'static/bootstrap3_datetime/js/locales/*.js',]},
    version='3.0',
    description='Bootstrap3 compatible datetimepicker for Django2/dPAC project.',
    long_description=open('README.rst').read(),
    author='David Pacheco',
    author_email='davidpch@gmail.com',
    url='https://github.com/david-pacheco/django-bootstrap3-datetimepicker.git',
    license='Apache License 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
)
