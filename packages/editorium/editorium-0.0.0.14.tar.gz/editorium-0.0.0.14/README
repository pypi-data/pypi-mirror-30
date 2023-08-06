Editorium
=========

Eᴅɪᴛᴏʀɪᴜᴍ creates Qᴛ editors for objects or functions via reflection.

Object fields or method parameters are reflected and an editor generated for each field or parameter.
For instance an `int` field is generated as a `QSpinBox` editor.

Please see the SᴛʀɪɴɢCᴏᴇʀᴄɪᴏɴ project for the command-line equivalent.

Features
--------

* Generate editor for field/type
* Generate editors for object
* Generate editors for function call
* Read fields from object to editors
* Write fields from editors into object
* Supports custom editors and extensions

Default editors
---------------

* `int` --> `QSpinBox`
* `str` --> `QLineEdit`
* `Optional` --> `QCheckBox`
* `bool` --> `QCheckBox` 
* `Enum` --> `QComboBox`
* `Flags` --> `QCheckBox` array
* `Filename` --> `QLineEdit` + `QToolButton`

### Notes

* `Optional[T]` is a _PEP-484_ annotation supplied by Pʏᴛʜᴏɴ's Tʏᴩɪɴɢ library and indicates that a value may be `None`.
* `Filename` is a _PEP-484_-style annotation provided by the MHᴇʟᴩᴇʀ library and provides hints on an acceptable filename e.g. `Filename[".txt", EMode.SAVE]`.

Meta
----

```ini
language=python,python3
type=lib
host=bitbucket,pypi
```