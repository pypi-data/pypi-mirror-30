================
pip-system-certs
================

This package patches pip at runtime to use certificates from the default system store (rather than the bundled certs ca).

This will allow pip to verify tls/ssl connections to servers who's cert is trusted by your system install.

Simply install with::

  pip install pip_system_certs

and pip should trust your hosts if your host system does.


Acknowledgements
----------------
The method of patching at runtime is built from the autowrapt module: https://pypi.python.org/pypi/autowrapt