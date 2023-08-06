from distutils.core import setup

setup(
    name='NL4Py',
    version='0.1.1',
    author='Chathika Gunaratne',
    author_email='chathikagunaratne@gmail.com',
    packages=['nl4py', 'nl4py.test'],
    scripts=['Demo_NL4Py.ipynb'],
    url='http://pypi.org/project/nl4py',
    license='GPL',
    description='A NetLogo connector for Python.',
    long_description=open('README.txt').read(),
	project_urls={
	'Source': 'https://github.com/chathika/NL4Py',
    'Say Thanks!': 'https://github.com/dmasad/Py2NetLogo',
    
	},
    install_requires=[
        'matplotlib >= 2.0.2',
        'py4j >= 0.10.6',
    ],
	python_requires='>=3',
)