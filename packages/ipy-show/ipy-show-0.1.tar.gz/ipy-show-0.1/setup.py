from setuptools import setup


setup(name="ipy-show",
      packages=["ipy_show"],
      license="BSD2CLAUSE",
      install_requires=['ipaddress'],
      scripts=['scripts/ipy-show'],
      version='0.1',
      description='A simple ip converter and stats.',
      long_description=("Convert an ip and maks in slash notation to binary. "
                        "Calcule the number max of hosts, number max of subnet"
                        " the network ip and broadast."),
      author='Silvio Ap Silva a.k.a Kanazuchi',
      author_email='contato@kanazuchi.com',
      url='http://github.com/kanazux/ipy-show',
      zip_safe=False)
