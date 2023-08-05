from setuptools import setup, find_packages

with open('requirements.txt') as file:
    requirements = file.read().splitlines()

setup(name='asyncjisho',
      author='BeatButton',
      url='https://github.com/BeatButton/asyncjiho',
      version='0.2.0',
      packages=find_packages(),
      license='MIT',
      description='An async wrapper for the Jisho.org API',
      include_package_data=True,
      install_requires=requirements,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
      ],
      )
