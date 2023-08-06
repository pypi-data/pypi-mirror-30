from distutils.core import setup


setup( name = "pyguisignal",
       url = "https://bitbucket.org/mjr129/pyguisignal",
       version = "0.0.0.8",
       description = "PyGuiSignal. Generate QT GUI and add missing signal handlers to code file.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["pyguisignal"],
       entry_points = { "console_scripts": ["pyguisignal = pyguisignal.__main__:main"] },
       python_requires = ">=3.6",
       install_requires = ["mhelper"]
       )
