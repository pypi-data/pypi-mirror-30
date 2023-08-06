from setuptools import setup

setup(
    name                        = "populater",
    packages                    = [
        "populater",
    ],
    package_dir                 = {
        "populater":		".",
    },
    install_requires            = [],
    version                     = "0.1.0",
    include_package_data        = True,
    author                      = "Matthew Brisebois",
    author_email                = "matthew@webheroes.ca",
    url                         = "https://github.com/webheroesinc/chaos-router",
    license                     = "Dual License; GPLv3 and Proprietary",
    description                 = "Cross platform string syntax for reliably extracting object data",
    long_description            = """
Cross platform string syntax for reliably extracting object data

===============
 Usage examples
===============

::

      import Populater
    
      Person = {
          "age": 17,
          "name": {
              "first": "Marty",
              "last": "Mcfly",
              "full": "Marty Mcfly"
          }
      }
      ctx				=  Populater( Person )
    
      assert ctx('{{ age }}')			== '17'
      assert ctx('< age')			== 17
      assert ctx('= {{ age }}')			== 17
      assert ctx("< name.first")		== "Marty"
      assert ctx("= {{ age }} > 18")		is True
      assert ctx("{{ name.none }}")		== ""
      assert ctx("= {{ name.none }}")		is None
      assert ctx(":= {{ name.full }}")		== "= Marty Mcfly"
      assert ctx("= '= {{ name.full }}'")	== "= Marty Mcfly"
      assert ctx(":: {{ name.full }}")		== ": Marty Mcfly"
      assert ctx("= self['name']['full']")	== "Marty Mcfly"

    """,
    keywords                    = [""],
    classifiers                 = [
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers"
    ],
)
