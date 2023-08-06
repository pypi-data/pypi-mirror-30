from setuptools import setup, find_packages 
setup(
    name = 'nebulaLogin',
    version = '0.3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
      ],
    license = 'MIT License',
    install_requires = ['python-ldap'],
 
    author = 'kevindwliu',
    author_email = 'kevindwliu@outlook.com',
    
    packages = find_packages(),
    platforms = 'any',
)
