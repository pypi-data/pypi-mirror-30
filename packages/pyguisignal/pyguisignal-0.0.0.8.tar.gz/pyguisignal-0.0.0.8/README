PyGuiSignal
===========

Simple script that parses source code and files made by Pʏᴜɪᴄ for PʏQᴛ5. It checks signal handlers are present in the source code and adds any missing ones.

What it does
------------
* Automatically scans folders and compiles dialogue designer (".ui") and resource (".qrc") files using `pyuic`.
* Parses the dialogue code (".py") files and adds missing signal handlers to the logic (".py") files.
* Flags invalid signal handlers.
* Moves window initialisation to the constructor of the dialogue class (PʏCʜᴀʀᴍ and Pʏʟɪɴᴛ don't like initialisation logic outside the constructor).
* Removes the `import resources_rc` from the dialogues (this only needs to be done once per application and causes problems in projects with subfolders).
* Generates a resource logic file, providing variable names for the contained resources (useful for autocomplete).

Default settings
----------------
* All settings can be configured, these are the default and represent a Vɪꜱᴜᴀʟ-Sᴛᴜᴅɪᴏ-esque file structure:
    * Resource designer files: `*.qrc`
    * Resource code files: `./*_rc.py` (relative to Resource designer files)
    * Resource logic files: `./*.py` (relative to Resource designer files)
    * Dialogue designer files: `*_designer.ui`
    * Dialogue code files: `./*_designer.py` (relative to Dialogue designer files)
    * Dialogue logic files: `../*.py` (relative to Dialogue designer files)
    * Move initialisation to constructor: `yes`
    * Remove `import resources_rc`: `yes`
    * Use PEP-484 annotations: `yes` 

Installation
------------

```bash
(sudo) pip install pyguisignal
```

Usage
-----

* Organise your project according to the [default settings](#default-settings) above or alter the [configuration](#configuration).

```bash
pyguisignal <path>
```

* `<path>` is the directory to scan, but you can also specify a single `ui` file if you want.
* If you are in the project root, `<path>` can be `.`
* You can pass more than one `<path>` or file at once.


Configuration
-------------

You can modify `~/.pyguisignal.json` (in the your home folder) to configure the application.

For convenience, the default `~/.pyguisignal.json` will be written when PʏGᴜɪSɪɢɴᴀʟ is first run.

Full documentation of all settings can be found in `configuration.py`.

However, as it's just a simple script, you can could also just edit the source code!


System requirements
-------------------

Should work on any system, but it's been tested on:

* Windows 7
* Kubuntu
* OSX

To avoid configurations for one machine not working on another, PʏGᴜɪSɪɢɴᴀʟ tries to fix the separators (`/`) you specify in paths, e.g. swapping `/` on Linux with `\` on Windows, but this might not work on all systems.

Meta
----

```ini
author      = martin rusilowicz
host        = bitbucket,pypi
url         = https://bitbucket.org/mjr129/pyguisignal
licence     = https://www.gnu.org/licenses/agpl-3.0.html
language    = python3
type        = application,cli
keywords    = pyqt,pyqt5,qt,python,gui,code,pyuic,pycharm,pylint
folder      = programming
```
