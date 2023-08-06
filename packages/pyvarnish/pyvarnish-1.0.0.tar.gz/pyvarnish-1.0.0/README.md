PyVarnish
=========

Lighweight Python interface for Varnish Manager

```python
  manager = VarnishManager(host="varnish.example.es")  # Default port is 6082
  manager.ping()
  manager.ban("req.http.host ~ www.example.es")
  manager.ban_url('^/secret/$')
  manager.ban_list()
  manager.command("<your custom command>")
  manager.quit()
```
