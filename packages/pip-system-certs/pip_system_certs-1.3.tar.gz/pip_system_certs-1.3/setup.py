import os
import sys
import distutils.sysconfig
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    long_description = readme.read()


def check_pth(site_packages):
    pthfile = os.path.join(site_packages, "pip_system_certs.pth")
    if not os.path.exists(pthfile):
        sys.stderr.write("WARNING: pip_system_certs.pth not installed correctly, will try to correct.\n")
        sys.stderr.write("Please report an issue at https://gitlab.com/alelec/pip-system-certs with your\n")
        sys.stderr.write("python and pip versions included in the description\n")
        import shutil
        shutil.copyfile("pip_system_certs.pth", pthfile)


class InstallCheck(install):
    def run(self):
        install.run(self)
        check_pth(self.install_purelib)


class DevelopCheck(develop):
    def run(self):
        develop.run(self)
        check_pth(self.install_dir)


site_packages = distutils.sysconfig.get_python_lib()

setup(
    name='pip_system_certs',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Live patches pip to use system certs by default',
    long_description=long_description,
    author='Andrew Leech',
    author_email='andrew@alelec.net',
    license='BSD',
    url='https://gitlab.com/alelec/pip-system-certs',
    packages=['pip_system_certs'],
    data_files=[(site_packages, ['pip_system_certs.pth'])],
    install_requires=['wrapt>=1.10.4', 'setuptools_scm'],
    zip_safe=False,
    cmdclass={"install": InstallCheck, "develop": DevelopCheck},
    python_requires='>=2.7.9, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
