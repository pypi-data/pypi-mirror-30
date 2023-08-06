from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from subprocess import check_call


class PostInstall(install):
    """Post installation steps.

    1. Install the notebook extension using jupyter nbextension install
    2. Enable the extension using jupyter nbextension enable
    """

    def run(self):
        # Do the usual install step
        install.run(self)

        # Register and install ourselves with jupyter
        check_call(["jupyter", "nbextension", "install",
                    "--py", "--symlink", "--sys-prefix", "topos.ext.preview"])
        check_call(["jupyter", "nbextension", "enable",
                    "--py", "--sys-prefix", "topos.ext.preview"])


def readme():
    with open("README.rst") as f:
        return f.read()


exec(open('topos/ext/preview/version.py', 'r').read())


setup(name='topos-preview',
      version=__version__,
      description="Widget for Jupyter Notebooks that allows for previewing topos Mesh objects",
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Multimedia :: Graphics'
      ],
      author='Alex Carney',
      author_email="alcarneyme@gmail.com",
      license='MIT',
      packages=['topos.ext.preview'],
      install_requires=[
          'numpy',
          'topos',
          'jupyter'
      ],
      setup_requires=['pytest-runner'],
      test_suite='tests',
      tests_require=['pytest', 'hypothesis'],
      cmdclass={
          'install': PostInstall
      },
      python_requires='>=3.0',
      include_package_data=True,
      zip_safe=False)
