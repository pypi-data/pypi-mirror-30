from distutils.core import setup

setup(name='Checks',
    py_modules = ['Checks'],
    version = '0.2', 
    url='https://github.com/CodeItISR/Python/tree/master/Frameworks/Checks',
    author='Netanel Prat',
    maintainer='Checks',
    keywords = ['testing', 'checking'],
    description = 'Easy and clean way to add conditions to function arguments',
    entry_points={
    'console_scripts':['Checks=Checks:main']},
    classifiers=[
    'Development Status :: 1 - Planning',
    'Environment :: Console',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6'])
