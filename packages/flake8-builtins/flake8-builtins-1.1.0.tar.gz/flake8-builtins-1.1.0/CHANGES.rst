.. -*- coding: utf-8 -*-

Changelog
=========

1.1.0 (2018-03-17)
------------------

- Update more trove classifiers.
  [gforcada]

- Inspect variables assigned in a for loop as well.
  Thanks to sobolevn for reporting it!
  [gforcada]

1.0.post0 (2017-12-02)
----------------------

- Update README.
  [DmytroLitvinov]

- Update trove classifiers.
  [dirn]

1.0 (2017-08-19)
----------------

- Use requirements.txt to pin dependencies.
  [gforcada]

- Fix tests with newer flake8 version.
  [gforcada]

- BREAKING CHANGE: error codes have been changed from B00X to A00X to not clash with flake8-bugbear,
  see https://github.com/gforcada/flake8-builtins/issues/7
  [gforcada]

0.4 (2017-05-29)
----------------

- Use a different code for class attributes.
  [karamanolev]

0.3.1.post0 (2017-05-27)
------------------------

- Release universal wheels, not only python 2 wheels.
  [gforcada]

- Update trove classifiers.
  [gforcada]

0.3.1 (2017-05-27)
------------------

- Fix stdin handling.
  [sangiovanni]

0.3 (2017-05-15)
----------------

- Handle stdin, which is the way flake8 gets integrated into editors.
  [gforcada]

- Test against Python 2.7, 3.5, 3.6 and pypy.
  [gforcada]

0.2 (2016-03-30)
----------------
- Whitelist *some* builtins.
  [gforcada]

0.1 (2016-03-04)
----------------
- Initial release
  [gforcada]

- Add buildout and other stuff.
  [gforcada]

- Add actual code.
  [gforcada]

- Drop support for python 3.3, only python 2.7 and python 3.4 are tested.
  [gforcada]
