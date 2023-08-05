* supports type 2 (setter) and type 3 (constructor) dependency injection
* can assemble *prototype*, *singleton*, *borg*, and *weakref* components
* supports templates (i.e. component inheritance) and lifecycle methods
* works with any kind of object creation pattern you'll encounter:
  * constructor
  * factory function or method
  * object creation hidden behind attribute or property access
* is configured declaratively, either programmatically through a fluent API or
  using a simple XML syntax (see the `Aglyph DTD
  <https://github.com/mzipay/Aglyph/blob/master/resources/aglyph-context.dtd>`_)
* is non-intrusive:
  * only one dependency (`Autologging
    <http://ninthtest.info/python-autologging/>`_) beyond the Python standard
    library
  * does not require modification of existing source code (i.e. no
    decorators, specific naming conventions, or any other kind of
    syntactic "magic" necessary)
* can inject not only 3rd-party dependencies, but also **dependents**
* runs on Python 2.7 and 3.4+ using the same codebase
* is proactively tested on `CPython <https://www.python.org/>`_,
  `Jython <http://www.jython.org/>`_, `IronPython <http://ironpython.net/>`_,
  `PyPy <http://pypy.org/>`_, and
  `Stackless Python <https://bitbucket.org/stackless-dev/stackless/wiki/Home>`_
* is fully logged *and traced* for ease of troubleshooting (note: tracing is
  disabled by default, and can be activated by setting an environment variable)


