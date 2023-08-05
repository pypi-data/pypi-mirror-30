from distutils.core import setup
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop


def _post_install():
    import subprocess
    from distutils import log
    log.set_verbosity(log.DEBUG)

    try:
        # Enable the required nbextensions for ipywidgets and nbtools
        subprocess.call(["jupyter", "nbextension", "enable", "--py", "widgetsnbextension"])
        subprocess.call(["jupyter", "nbextension", "install", "--py", "nbtools"])
        subprocess.call(["jupyter", "nbextension", "enable", "--py", "nbtools"])

        # Enable the GenePattern Notebook extension
        subprocess.call(["jupyter", "nbextension", "install", "--py", "genepattern"])
        subprocess.call(["jupyter", "nbextension", "enable", "--py", "genepattern"])
        subprocess.call(["jupyter", "serverextension", "enable", "--py", "genepattern"])
    except:
        log.warn("Unable to automatically enable GenePattern extension for Jupyter.\n" +
                 "Please manually enable the extension by running the following commands:\n" +
                 "jupyter nbextension enable --py widgetsnbextension\n" +
                 "jupyter nbextension install --py genepattern\n" +
                 "jupyter nbextension enable --py genepattern\n" +
                 "jupyter serverextension enable --py genepattern\n")


class GPInstall(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, [], msg="Running post install task")


class GPDevelop(_develop):
    def run(self):
        _develop.run(self)
        self.execute(_post_install, [], msg="Running post develop task")


setup(name='genepattern-notebook',
      packages=['genepattern'],
      version='0.7.1',
      description='GenePattern Notebook extension for Jupyter',
      license='BSD',
      author='Thorin Tabor',
      author_email='tmtabor@cloud.ucsd.edu',
      url='https://github.com/genepattern/genepattern-notebook',
      download_url='https://github.com/genepattern/genepattern-notebook/archive/0.7.1.tar.gz',
      keywords=['genepattern', 'genomics', 'bioinformatics', 'ipython', 'jupyter'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Developers',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Framework :: Jupyter',
      ],
      install_requires=[
          'genepattern-python>=1.2.3',
          'nbtools',
          'jupyter',
          'notebook>=4.2.0',
          'ipywidgets>=5.0.0',
      ],
      cmdclass={'install': GPInstall, 'develop': GPDevelop},
      package_data={'genepattern': ['static/index.js', 'static/resources/*']},
      )
