from setuptools import setup, find_packages
from distutils.core import setup


setup(name='external-user-provision-tool',
      version='1.22',
      description='Add and remove users from multiple web services with desired permissions',
      url='https://github.com/Signiant/External-user-provisioning',
      author='Eric Laroche',
      author_email='elaroche@signiant.com',
      license='MIT',
      entry_points = {
        "console_scripts": ['userprovision = project.user_provision:main']
        },
      packages=find_packages(),
      install_requires=[
        "azure.graphrbac",
        "msrestazure",
        
       ],
      zip_safe=False)
