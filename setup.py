from setuptools import setup, find_packages

setup( name='session-cart',
    version='1.2.0',
    description='A session-stored cart for Django',
    author='Curtis Maloney, Grigoriy Bezyuk, Nestor Diaz',
    author_email='curtis@tinbrain.net, gbezyuk@gmail.com, nestor@coobleiben.coop',
    url='https://github.com/n3storm/session_cart',
    keywords=['django', 'cms', 'e-commerce',],
    packages=find_packages(),
    zip_safe=False,
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
