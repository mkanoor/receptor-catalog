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
 3. **accept_encoding** *{Optional}*: gzip
 4. **fetch_all_pages** *{Optional}*: True|False 
 5. **params**: Extra query or post parameters as a hash/dictionary
 6. **apply_filter** *{Optional}*: A JMESPath search string to limit the amount of data that is returned. The filter can be specified as a hash/dictionary or as a string. The hash is used when filtering responses from a list call when the response contains an array of objects. The string filter is used when dealing with a single object.


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


**Filtering Examples**
Filters are based on JMESPath which allows us to search and filter out sections of JSON.
https://jmespath.org
When fetching an array of objects you have to specific the filter as a dictionary with the key name containing the name of the attribute.
e.g
**apply_filter*** ={results=**'results[].{catalog_id:id, url:url,created:created,name:name, modified:modified, playbook:playbook}'**}

The response contains
```

{

"count": 28,

"next": "/api/v2/job_templates/?page=2",

"previous": null,

"results": [

{

"catalog_id": 5,

"url": "/api/v2/job_templates/5/",

"created": "2019-05-29T15:17:05.466994Z",

"name": "Demo Job Template",

"modified": "2019-05-29T15:17:05.467018Z",

"playbook": "hello_world.yml"

},

{

"catalog_id": 58,

"url": "/api/v2/job_templates/58/",

"created": "2020-03-06T21:56:55.134663Z",

"name": "Ephemeral Template",

"modified": "2020-03-06T22:15:15.655800Z",

"playbook": "hello_world.yml"

},
```

When a single object needs to be filtered we specify the filter as a string

apply_filter = **'{id:id, url:url, name:name, description:descripti  on, playbook:playbook}'**

The response contains
```
{

"id": 6565,

"url": "/api/v2/jobs/6565/",

"name": "Hello World",

"description": "Test Description",

"playbook": "hello_world.yml"

}
```
