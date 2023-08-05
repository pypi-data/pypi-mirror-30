from setuptools import setup

setup(name='chff',
      version='0.1.4',
      install_requires=[
        "aiortc",
      ],
      description='Overlay Network Reference Implementation',
      classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Security :: Cryptography',
      ],
      url='http://github.com/mnes-io/chff',
      author='Charles Perkins',
      author_email='charlesap@gmail.com',
      license='MIT',
      packages=['chff'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
