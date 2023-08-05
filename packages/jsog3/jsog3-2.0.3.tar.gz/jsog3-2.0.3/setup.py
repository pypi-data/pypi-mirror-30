

from setuptools import setup, find_packages
setup(
	name='jsog3',
	version='2.0.3',
    packages=['jsog3'],
	author='Simon Eggler',
	author_email='simon.eggler@gmx.net',
	url='https://github.com/simoneggler/jsog-python',
	description='JSOG serializer and deserializer',
	keywords='jsog json',
	license='MIT License',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3'
	],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.md'],
    },

    # metadata for upload to PyPI
    project_urls={
        "Bug Tracker": "https://github.com/simoneggler/jsog-python/issuespython",
        "Documentation": "https://github.com/simoneggler/jsog-python/wiki",
        "Source Code": "https://github.com/simoneggler/jsog-python",
    }

    # could also include long_description, download_url, classifiers, etc.

)
