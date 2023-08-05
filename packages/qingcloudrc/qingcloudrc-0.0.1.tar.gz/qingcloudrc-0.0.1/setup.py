#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages 
VERSION = '0.0.1'
setup(name='qingcloudrc',
      version=VERSION,
      description="Python",
      long_description='just enjoy',
      classifiers=[],
      keywords='python',
      author='ztt',
      author_email='zttjava@qq.com',
      url='https://github.com/xxx',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      entry_points={
        'console_scripts':[
            'qingcloudrc = qingcloudrc.qingcloudrc:run_instance'
        ]
      }
)