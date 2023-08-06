PyVarnish
=========

Lighweight Python interface for Varnish Manager

Tested with Varnish 4.x.x and 5.x.x

### Instalation:
```bash
pip install pyvarnish
```

### Example:

```python
# Default port is 6082 and secret is an optional parameter
  manager = VarnishManager(host="varnish.example.es", port=80, secret="MySecret")
  manager.ping()
  manager.ban("req.http.host ~ www.example.es")
  manager.ban_url('^/secret/$')
  manager.ban_list()
  manager.command("<your custom command>")
  manager.quit()
```

Others:
-------

Based on [justquick/python-varnish](https://github.com/justquick/python-varnish) library
