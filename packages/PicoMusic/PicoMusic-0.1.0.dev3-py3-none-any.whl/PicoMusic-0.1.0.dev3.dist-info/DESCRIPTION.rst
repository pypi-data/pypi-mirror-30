PicoMusic
=========

A tiny audiovisual music tool for Python.




Purpose
-------

PicoMusic is a tool for learning about Python and music,
by composing music with Python.


Design goals
------------

-   Simple: to help you learn about programming and music composition.

-   Pythonic: transfer what you learn to non-musical projects.

-   Expressive: enough to create compelling audiovisual masterpieces.

-   Finished projects can be exported and shared.

-   Runs comfortably on macOS, Windows, and Linux (including Raspbian on Raspberry Pi 3).

Changelog
=========


0.1.0 series
------------

This is the initial release of PicoMusic.


0.1.0.dev3 (2018-03-18)
-----------------------

Changes
.......

- Simplify ``Pitch.__repr__()`` for better use within tutorials.

- Add full ``Fraction`` name to interactive namespace,
  so that the repr of a Fraction instance can be entered to get that fraction.

- Fix ``Note.__repr__()`` to be consistently formatted.

- Documentation improvements.

Fixes
.....

- Reduce size of BasicKit by trimming silence from end of samples.


0.1.0.dev2 (2018-03-11)
-----------------------

Fixes
.....

- Correct the singleton implementation of ``StageManager``.

- Add all package requirements.

- Include package requirements in ``setup.py``.


0.1.0.dev1 (2018-03-11)
-----------------------

- Initial release.


