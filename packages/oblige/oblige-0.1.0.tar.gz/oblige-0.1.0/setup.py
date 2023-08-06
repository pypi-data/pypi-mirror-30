import sys, os, subprocess, sysconfig
from distutils import sysconfig
from distutils.command.build import build
from multiprocessing import cpu_count
from setuptools import setup
import glob

platform = sys.platform
supported_platforms = ["Linux", "Mac OS-X"]
package_path = "pyoblige"
oblige_src_path = "Oblige_src"
if platform.startswith("win"):
    raise RuntimeError("Building pip package on Windows is not currently available ...")
elif platform.startswith("darwin"):
    makefile = "Makefile.macos"
elif platform.startswith("linux"):
    makefile = "Makefile"
else:
    raise RuntimeError("Unrecognized platform: {}".format(sys.platform))


class BuildCommand(build):
    def run(self):
        try:
            pass
            src_path = os.path.realpath(os.path.realpath(
                os.path.join(os.path.dirname(__file__), os.path.join(package_path, oblige_src_path))))
            subprocess.check_call(["make", "-f", makefile], cwd=src_path)
        except subprocess.CalledProcessError:
            sys.stderr.write("\033[1m\nInstallation failed, you may be missing some dependencies. "
                             "\nPlease check https://github.com/mwydmuch/PyOblige/README.md for details\n\n\033[0m")
            raise
        build.run(self)


extra_files = [x.replace('pyoblige/', "") for x in glob.glob("pyoblige/Oblige_src/**", recursive=True)]
setup(
    name='oblige',
    version='0.1.0',
    description='TODO',
    long_description="TODO",
    url='https://github.com/mwydmuch/PyOblige',
    author='Marek Wydmuch, Michał Kempka',
    author_email='vizdoom@googlegroups.com',
    packages=['oblige'],
    package_dir={'oblige': package_path},
    package_data={'oblige': ["Oblige_src/Oblige", ] + extra_files},
    include_package_data=True,
    cmdclass={'build': BuildCommand},
    platforms=supported_platforms,
    classifiers=[
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        # 'License :: OSI Approved :: MIT License',  # ??
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
