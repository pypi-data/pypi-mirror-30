from setuptools import setup, find_packages

setup(name='pyutils_sh',
      version='1.1.0',
      description='Assortment of Python utilities for my personal projects',
      url='https://github.com/sho-87/pyutils_sh',
      author='Simon Ho',
      author_email='simonho213@gmail.com',
      license='MIT',
      packages=find_packages(),
      python_requires='>=3',
      install_requires=['numpy', 'pandas'],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
      ],
      keywords='python utilities survey exam gaze spss data research statistics',
      zip_safe=True)