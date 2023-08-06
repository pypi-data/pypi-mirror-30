from setuptools import setup
def readme():
    with open('README.rst') as f:
        return f.read()



setup(name='uetla',
      version='0.3',
      description='UET Analytic for Moodle',
      long_description=readme(),
      keywords='Learning analytics',
      url='https://github.com/NguyenBach/UETBackend.git',
      author='Bach Nguyen',
      author_email='bachnq214@gmail.com',
      packages=['uetla'],
      install_requires=[
          'scikit-learn >= 0.19.1',
          'pandas >= 0.22.0',
          'mysqlclient >= 1.3.12',
          'scipy >= 1.0.0'
      ],
      include_package_data=True,
      zip_safe=False)