from setuptools import setup, find_packages
import io

from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('snarky/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst')

setup(
    name='snarky',
    version=main_ns['__version__'],
    url='https://github.com/eackermann/snarky/',
    download_url = 'https://github.com/eackermann/snarky/tarball/' + main_ns['__version__'],
    license='MIT License',
    author='Etienne Ackermann',
    install_requires=['google_speech>=1.0.0', # for speech synthesis
                    ],
    author_email='era3@rice.edu',
    description="Snarky adds a 'jk' (just kidding!) keyword argument to any function.",
    long_description=long_description,
    packages=find_packages(),
    keywords = "useless kidding",
    include_package_data=True,
    platforms='any'
)

# @misc{Ackermann2017,
#         author = {Etienne Ackermann},
#         title = {snarky},
#         year = {2018},
#         publisher = {GitHub},
#         journal = {GitHub repository},
#         howpublished = {\url{https://github.com/eackermann/snarky}},
#         commit = {enter commit that you used}
# }