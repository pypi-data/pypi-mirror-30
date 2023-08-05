

Run the Tests
-------------

Install tox and run it::

    pip install tox
    tox

Limit the tests to a specific python version::

    tox -e py27

Conventions
-----------

Onegov Foundation follows PEP8 as close as possible. To test for it run::

    tox -e pep8

Onegov Foundation uses `Semantic Versioning <http://semver.org/>`_

Build Status
------------

.. image:: https://travis-ci.org/OneGov/onegov.foundation.png
  :target: https://travis-ci.org/OneGov/onegov.foundation
  :alt: Build Status

Coverage
--------

.. image:: https://coveralls.io/repos/OneGov/onegov.foundation/badge.png?branch=master
  :target: https://coveralls.io/r/OneGov/onegov.foundation?branch=master
  :alt: Project Coverage

Latests PyPI Release
--------------------
.. image:: https://img.shields.io/pypi/v/onegov.foundation.svg
  :target: https://crate.io/packages/onegov.foundation
  :alt: Latest PyPI Release

License
-------
onegov.foundation is released under GPLv2

Changelog
---------

0.4.1 (2018-03-26)
~~~~~~~~~~~~~~~~~~~

- Possibly fixes unrecognized expression errors in some browsers.
  [href]

- Requires Python 3.6.
  [href]

0.4.0 (2017-10-25)
~~~~~~~~~~~~~~~~~~~

- Replaces rcssmin/pyscss with the dramatically faster libsass.
  [href]

0.3.0 (2017-07-10)
~~~~~~~~~~~~~~~~~~~

- Replace csscompress with rcssmin, which produces slightly bigger results but
  does so in a much faster way.
  [href]

0.2.0 (2017-01-11)
~~~~~~~~~~~~~~~~~~~

- Adds the ability to limit the number of used foundation components.
  [href]

0.1.1 (2016-06-20)
~~~~~~~~~~~~~~~~~~~

- Removes the custom pyscss monkey patch, as the issues has been resolved.
  [href]

0.1.0 (2015-10-12)
~~~~~~~~~~~~~~~~~~~

- Removes Python 2.x support.
  [href]

0.0.4 (2015-07-13)
~~~~~~~~~~~~~~~~~~~

- Monkey-patches pyscss, to fix its Zurb Foundation compilation.
  See https://github.com/Kronuz/pyScss/pull/342.
  [href]

0.0.3 (2015-06-26)
~~~~~~~~~~~~~~~~~~~

- Adds support for onegov.core.upgrade
  [href]

- Remove support for Python 3.3
  [href]

0.0.2 (2015-05-05)
~~~~~~~~~~~~~~~~~~~

- Upgrade to Zurb Foundation 5.5.2.
  [href]

0.0.1 (2015-04-29)
~~~~~~~~~~~~~~~~~~~

- Initial Release.
  [href]


