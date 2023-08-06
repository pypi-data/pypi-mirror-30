from setuptools  import setup

setup(
    name='NL4Py',
    version='0.1.3',
    author='Chathika Gunaratne',
    author_email='chathikagunaratne@gmail.com',
    packages=['nl4py', 'nl4py.test'],
    url='http://pypi.org/project/nl4py',
    license='GPL',
    description='A NetLogo connector for Python.',
    long_description=open('README.txt').read(),
	project_urls={
	'Source': 'https://github.com/chathika/NL4Py',
    'Thanks!': 'https://github.com/dmasad/Py2NetLogo',
    'Thanks!': 'http://complexity.cecs.ucf.edu/',
	},
    install_requires=[
        'matplotlib >= 2.0.2',
        'py4j >= 0.10.6',
    ],
	python_requires='>=3',
)

