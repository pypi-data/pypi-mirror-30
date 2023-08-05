from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
long_descrption = ""
with open(here + "/README.md", "r") as readme:
	long_descrption = readme.read()

setup(
    name='tsu4lape',  # Required
    version='0.1',  # Required
    description='A simple test suite for lazy people',  # Required
	long_descrption = long_descrption,
    url='https://github.com/Bstiler/Tsu4Lape',  # Optional
    author='Bstiler',  # Optional
    author_email='Bruno08new12@gmail.com',  # Optional
    # classifiers=[  # Optional
    #     'Development Status :: 3 - Alpha',
    #     'Intended Audience :: Developers',
    #     'Topic :: Software Development :: Test Tools',
    #     'License :: LGPL3 License',
    #     'Programming Language :: Python :: 3',
    # ],
	python_requires='>=3',
    keywords='test setuptools development',  # Optional
    py_modules=["tsu4lape"],
	install_requires=['demjson'],  # Optional
    package_data={  # Optional
        'schema': ['tsu4lape.json'],
    },
    project_urls={  # Optional
        'Source': 'https://github.com/Bstiler/Tsu4Lape',
    },
)
