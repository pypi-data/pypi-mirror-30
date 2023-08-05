from setuptools import setup

setup(name='chff',
      version='0.1.1',
      install_requires=[
        "aiortc",
      ],
      description='Overlay Network Reference Implementation',
      url='http://github.com/mnes-io/chff',
      author='Charles Perkins',
      author_email='charlesap@gmail.com',
      license='MIT',
      packages=['chff'],
      zip_safe=False)
