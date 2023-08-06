Changelog
=========

5.0 (2018-04-13)
----------------

- Remove dysfunctional LowConflictConnection.

- Add support for Python 3.4, 3.5 and 3.6.

4.0 (2016-08-02)
----------------

- Add in code of `Products.TemporaryFolder` and `Products.ZODBMountPoint`.

- Require `Zope >= 4`.

3.0 (2016-08-02)
----------------

- Create a separate distribution called `Products.TemporaryFolder` without
  any code inside it. This allows projects to depend on this project
  inside the Zope 2.13 release line.
