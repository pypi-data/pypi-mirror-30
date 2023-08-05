from setuptools import setup, find_packages


setup(
    name='deeppages',
    version='0.1.1',
    description="Django's database stored web content processor",
    url='https://github.com/ricardofalasca/deep-pages',
    author='Ricardo Falasca',
    author_email='ricardo@falasca.com.br',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
