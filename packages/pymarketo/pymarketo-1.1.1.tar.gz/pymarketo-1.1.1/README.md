PyMarketo
===================

Python Client that covers the complete Marketo REST API. It handles authentication, error handling, rate limiting
to the standard limit of 100 calls in 20 seconds (defined in http_lib module) ~_and bulk exports_~(bulks export has been added to base marketorestpython project instead) while providing a simpler interface to its audience. This is an _extension_ to the [marketo-rest-python](https://github.com/jepcastelein/marketo-rest-python) project.<br />


Full Marketo REST API documentation can be referenced [here](http://developers.marketo.com/documentation/rest/).
<br/>

Installation
============
```bash
pip install pymarketo
```

Usage
=====
```python
from pymarketo import Marketo
munchkin_id = "" # fill in server id from Admin > Web Services, typical format 000-AAA-00
client_id = "" # enter Client ID from Admin > LaunchPoint > View Details
client_secret= "" # enter Client ID and Secret from Admin > LaunchPoint > View Details
mkto = Marketo(munchkin_id, client_id, client_secret)
```

> More documentation about helper methods and access to `marketorestpython` methods to come here.