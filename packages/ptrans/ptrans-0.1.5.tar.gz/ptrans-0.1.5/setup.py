from setuptools import setup, find_packages

VERSION = '0.1.5'

setup(name='ptrans',
      version=VERSION,
      description="A command line tool help you translate other lauguages to Chinese each other",
      long_description='',
      keywords='translate terminal',
      author='linrz',
      author_email='1246533834@qq.com',
      url='https://github.com/linrz/translate-tool',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'requests',
      ],
      entry_points={
        'console_scripts': [
            'trans = trans.main:main'
        ]
      },
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5'
      ]
)
