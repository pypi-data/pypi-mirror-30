from setuptools import setup

setup(name='network-cli',
      version='0.1',
      description='network-probe-tool',
      url='https://github.com/amardeep-programmer/network-prober',
      author='amardeep singh',
      author_email='amars123456@gmail.com',
      license='MIT',
      script=['network-cli'],
      install_requires=[
          'sh',
          'colorama'
      ],
      zip_safe=False)