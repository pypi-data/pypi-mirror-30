from distutils.core import setup


setup( name = "prdoc",
       url = "https://bitbucket.org/mjr129/prdoc",
       version = "1.0.0.6",
       description = "Print a markdown file to the terminal.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["prdoc"],
       entry_points = { "console_scripts": ["prdoc = prdoc.__main__:main"] },
       install_requires = ["mhelper"],
       python_requires = ">=3.6"
       )
