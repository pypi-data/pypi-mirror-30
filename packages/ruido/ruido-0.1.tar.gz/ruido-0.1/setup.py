from setuptools import setup
from setuptools_rust import Binding, RustExtension

# Workaround from https://github.com/PyO3/setuptools-rust/issues/2
try:
    from setuptools_rust import Binding, RustExtension
except ImportError:
    import os, subprocess, sys
    try:
        subprocess.check_call([sys.executable, '-m', 'pip',
                               'install', 'setuptools-rust'])
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    except subprocess.CalledProcessError as err:
        print("Please install setuptools-rust package")
        raise SystemExit(err.errno)

setup(name='ruido',
      version='0.1',
      rust_extensions=[RustExtension('ruido._ruido',
                                     'Cargo.toml',
                                     binding=Binding.RustCPython)],
      packages=['ruido'],
      # rust extensions are not zip safe, just like C-extensions.
      zip_safe=False)
