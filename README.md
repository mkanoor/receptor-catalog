# receptor-catalog
Receptor Catalog Worker Plugin

This plugin allows the receptor node to send HTTP **GET** and **POST** requests
to Ansible Tower.

The config file on the receptor for this plugin should have the following values defined in the receptor.conf

```
[plugin_receptor_catalog]
debug=True
username=admin
password=******
url=https://your_ansible_tower/
verify_ssl=False
```

The payload supported by the plugin contains

 1. **method:** GET|POST
 2. **href_slug**: the href to the resource or collection e.g api/v2/job_templates/
 3. **accept-encoding**: gzip
 4. **fetch_all_pages**: True|False
 5. **params**: Extra query or post parameters as a hash/dictionary

The response payload coming back will have the following keys

 1. **status**: The HTTP Status code
 2. **body**:  The response body received from the Ansible Tower
       if Accept-Encoding was gzip, the body will be compressed and
       the caller would have to uncompress the data. The first 2 bytes
       of the payload can be checked to see if the data has been gzip
       compressed. A valid gzip'ed buffer would start with ***0x1f 0x8B*** 

To install the plugin in your local dev environment

**python setup.py install**

To run the tests

**python setup.py test**
