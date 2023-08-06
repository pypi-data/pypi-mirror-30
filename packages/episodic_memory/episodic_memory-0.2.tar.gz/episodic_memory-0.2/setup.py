from setuptools import setup, find_packages

setup(name='episodic_memory',
      version='0.2',
      description='an episodic memory module',
      keywords='psychology memory',
      url='https://github.com/qihongl/episodic_memory',
      author='Qihong Lu',
      author_email='lvqihong1992@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'numpy',
      ],
      zip_safe=False)

