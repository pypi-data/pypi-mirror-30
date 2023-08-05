Hatchbuck.com CRM API bindings for python
===========================================
This python package provides an easy to use python module to interact with the `hatchbuck.com API <https://hatchbuck.freshdesk.com/support/solutions/articles/5000578765-hatchbuck-api-documentation-for-advanced-users>`_

Installation
--------------
The easiest way to install hatchbuck is with pip

.. code::

    $ pip install hatchbuck

Basic Usage
------------

.. code-block::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.search_email('bashar.said@vshn.ch')
    pp.pprint(profile)

You can get your Hatchbuck API key at https://app.hatchbuck.com/Account/UpdateAPIKey when logged in

Examples
---------
Search for one email address
-----------------------------

.. code:: python

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.search_email('bashar.said@vshn.ch')
    pp.pprint(profile)


output
--------
.. code::

    {'addresses': [{'city': 'Zürich',
                'country': 'Switzerland',
                'countryId': 'QmJzeldzQ25rbXluZGc4RzlDYmFmYlZOY2xTemMwX2ZoMll5UTJPenhsNDE1',
                'id': 'Q0NjajF2U1lTWnBHM1hjRFlnQzhzMHZ2UUxLY2d6a1JaU3Nicm5hRTN6azE1',
                'state': 'ZH',
                'street': 'Neugasse 10',
                'type': 'Work',
                'typeId': 'SjFENlU0Y2s2RDFpM0NKWEExRmVvSjZ4T3NJMG5pLWNYZjRseDBSaTVfVTE1',
                'zip': '8005'}],
 'campaigns': [],
 'company': 'VSHN AG',
 'contactId': 'SUFYbGdOaEQ0cWR2N1JfV183UFNBSDllTktCc3E3OWRsN09qaW4tU3JqbzE1',
 'customFields': [{'name': 'Comments', 'type': 'MText', 'value': ''},
                  {'name': 'Invoiced', 'type': 'Number', 'value': ''},
                  {'name': 'Language', 'type': 'Text', 'value': ''},
                  {'name': 'working at company since',
                   'type': 'Text',
                   'value': '1.1.2018'},
                  {'name': 'company size', 'type': 'Text', 'value': '25'},
                  {'name': 'Birthday', 'type': 'Date', 'value': ''}],
 'emails': [{'address': 'bashar.said@vshn.ch',
             'id': 'S2lIY2NOS2dBRnRCamEyQUZxTG00dzhlYjAxUU9Sa3Z5ZFVENGVHTG1DODE1',
             'type': 'Work',
             'typeId': 'VmhlQU1pZVJSUFFJSjZfMHRmT1laUmwtT0FMNW9hbnBuZHd2Q1JTdE0tYzE1'}],
 'firstName': 'Bashar',
 'instantMessaging': [],
 'lastName': 'Said',
 'phones': [{'id': 'OHh4U0ZWc3FNVXVBQVF4cjdsak9McWc4TVppZlF4NklrNmZfSnBhaDZwQTE1',
             'number': '+(414) 454-5 53 00',
             'type': 'Work',
             'typeId': 'QTBncHV0dndnaGNnRVMzLTR0SGtFRmRvZjdqNm4zcVphQi1XX1Z2MXVtRTE1'}],
 'referredBy': '',
 'salesRep': {'id': 'VGpwQTRGTmw4MExVODl1b1BmXzBodTBwWnZXS2dUZzVvSkJKZUx4UlFpdzE1',
              'username': 'aarno.aukia'},
 'socialNetworks': [{'address': 'https://twitter.com/bashar_2018',
                     'id': 'S1pEM2NMWlhmZ1VUcDhTUWVvQy1kU21xMjlSbDg5Z3piMERVbEFsam42azE1',
                     'type': 'Twitter',
                     'typeId': 'ZGRlMHpBaXY3M05YUGc4a0pIY3lRdUFKN1JYaDd2VEphbzhSRkdzM2x4bzE1'},
                    {'address': 'https://www.linkedin.com/in/bashar-said-729a54156/',
                     'id': 'Tzd0TTBueVQzS09JQVZTLUxiUUxUT25VMmVvT0dua2txc2NHZkNkNEg5VTE1',
                     'type': 'LinkedIn',
                     'typeId': 'Q2dJTVQ1NW9UYzhJeUd4ckI0dWFNWkpLOUxyTXVGUFVjQlZYbVM2ZlI4bzE1'}],
 'source': {'id': 'MHZFdHZqcWVXT1IyNHZGYlM1RGppWVVJcGc3aHgtU3lXRWtfQmFXN0lCODE1',
            'name': 'vshn.ch'},
 'status': {'id': 'UE9zMy1abnhnNUJQWnVORE5BQzNicUFWQ3huLXF2eGlSdlIyYVFmVXh4UTE1',
            'name': 'Employee'},
 'subscribed': True,
 'tags': [],
 'temperature': {'id': 'UTI0Nm14TlB4SmRkdVNLMjNWQWgwR2R2TjhySE1US1RtVEQ0T24tRWtFbzE1',
                 'name': 'Hot'},
 'timezone': 'W. Europe Standard Time',
 'title': 'DevOps Engineer Intern',
 'website': [{'id': 'bktodFBCalVCU2J6aFhjaXc5UVZkUHM5OHFnd0ZuQmdJTTU0cDRScm1KSTE1',
              'websiteUrl': 'https://vshn.ch'}]}



Search for the first and last name
------------------------------------
.. code::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.search_name('bashar', 'said')
    pp.pprint(profile)


output
-------
.. code-block::

    We get the same results When we search by email address because the firstname and lastname(bashar, said) belong to the         same email address(bashar.said@vshn.ch)


Search within a list of email addresses
----------------------------------------
.. code::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.search_email_multi(['sgdhfgfdgh@fdvd.com', 'bashar.said@vshn.ch', ...])
    pp.pprint(profile)


**Note:** The emails must be in list form, and the search process stops getting the first match

output
-------

.. code::

    2018-03-08 11:00:21,079 - hatchbuck - DEBUG - searching for {'emails': [{'address': 'sgdhfgfdgh@fdvd.com'}]}
    2018-03-08 11:00:21,091 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTPS connection (1):     api.hatchbuck.com
    2018-03-08 11:00:21,857 - requests.packages.urllib3.connectionpool - DEBUG - "POST /api/v1/contact/search?
    2018-03-08 11:00:21,860 - hatchbuck - DEBUG - not found


**We did not find a profile with an email address: 'sgdhfgfdgh@fdvd.com'**

.. code::

    2018-03-08 11:00:21,860 - hatchbuck - DEBUG - searching for {'emails': [{'address': 'bashar.said@vshn.ch'}]}
    2018-03-08 11:00:21,862 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTPS connection (1):     api.hatchbuck.com
    2018-03-08 11:00:22,641 - requests.packages.urllib3.connectionpool - DEBUG - "POST /api/v1/contact/search?
    2018-03-08 11:00:22,643 - hatchbuck - DEBUG - found: {......}


**We found a profile with his email address: 'bashar.said@vshn.ch'**

output
-------

**We get the same results When we search by email address**


Create profile
----------------
.. code::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.create({
        "firstName": "Hawar",
        "lastName": "Afrin",
        "title": "Hawar1",
        "company": "HAWAR",
        "emails": [
            {
                "address": "bashar.said.2018@gmail.com",
                "type": "work",
            }
        ],
        "phones": [
            {
                "number": "0041 76 803 77 34",
                "type": "work",
            }
        ],
        "status": {
            "name": "Employee",
        },
        "temperature": {
            "name": "Hot",
        },
        "addresses": [
            {
                "street": "Langäcker 12",
                "city": "wettingen",
                "state": "AG",
                "zip": "5430",
                "country": "Schweiz",
                "type": "work",
            }
        ],
        "timezone": "W. Europe Standard Time",
        "socialNetworks": [
            {
                "address": "'https://twitter.com/bashar_2018'",
                "type": "Twitter",
            }
        ],
    })
    pp.pprint(profile)


output
-------
.. code::

   {'addresses': [{'city': 'Wettingen',
                'country': 'Switzerland',
                'countryId': 'QmJzeldzQ25rbXluZGc4RzlDYmFmYlZOY2xTemMwX2ZoMll5UTJPenhsNDE1',
                'id': 'eDZNV2d4Q1ZIR09UN2p1UlhzclVCdTM0LU81UW5TZzZmU05vLUtuVzdoMDE1',
                'state': '',
                'street': 'Langäcker 13',
                'type': 'Home',
                'typeId': 'M1ZkLXI3UnJqUWxUVDNFZUZ3MW5MdG5KSGZuN0lVemNDcXNLdzgzbjBDVTE1',
                'zip': '5430'},
               {'city': 'Zürich',
                'country': 'Switzerland',
                'countryId': 'QmJzeldzQ25rbXluZGc4RzlDYmFmYlZOY2xTemMwX2ZoMll5UTJPenhsNDE1',
                'id': 'OEFPUzJBeTdaWlVhU3FDR194dEk3NU8xTThxakZuQXV4aE9obHM3SVdKTTE1',
                'state': 'ZH',
                'street': 'Neugasse 10',
                'type': 'Work',
                'typeId': 'SjFENlU0Y2s2RDFpM0NKWEExRmVvSjZ4T3NJMG5pLWNYZjRseDBSaTVfVTE1',
                'zip': '8005'},
               {'city': 'Wettingen',
                'country': 'Switzerland',
                'countryId': 'QmJzeldzQ25rbXluZGc4RzlDYmFmYlZOY2xTemMwX2ZoMll5UTJPenhsNDE1',
                'id': 'QnZnaFlQYlhnU0NZX0x6NHZMVTJoaU9HV1AzS0dybjdOd0JDc1AwVlVXMDE1',
                'state': '',
                'street': 'Langäcker',
                'type': 'Home',
                'typeId': 'M1ZkLXI3UnJqUWxUVDNFZUZ3MW5MdG5KSGZuN0lVemNDcXNLdzgzbjBDVTE1',
                'zip': '5430'}],
 'campaigns': [],
 'contactId': 'TmpmT0QyUGE3UGdGejZMay1xbDNyUHJFWU91M2VwN0hCdGtZZFFCaWRZczE1',
 'customFields': [{'name': 'Comments', 'type': 'MText', 'value': ''},
                  {'name': 'Invoiced', 'type': 'Number', 'value': ''},
                  {'name': 'Language', 'type': 'Text', 'value': ''},
                  {'name': 'working at company since',
                   'type': 'Text',
                   'value': ''},
                  {'name': 'company size', 'type': 'Text', 'value': ''},
                  {'name': 'Birthday', 'type': 'Date', 'value': '1/1/1984'}],
 'emails': [{'address': 'bashar.said.2018@gmail.com',
             'id': 'M2FaYWpqY1pBMldGeVpYYW11cXRpTUw2NndOcFJsUXIzZGI2VC1JRmdSYzE1',
             'type': 'Work',
             'typeId': 'VmhlQU1pZVJSUFFJSjZfMHRmT1laUmwtT0FMNW9hbnBuZHd2Q1JTdE0tYzE1'}],
 'firstName': 'Hawar',
 'instantMessaging': [],
 'lastName': 'Afrin',
 'phones': [{'id': 'MVhxaXBHdlRWOWdLX05FbHF6ZnczMERGVTMyWWRkZ0xsSFFQcXVNYW5NTTE1',
             'number': '0041 76 803 77 34',
             'type': 'Work',
             'typeId': 'QTBncHV0dndnaGNnRVMzLTR0SGtFRmRvZjdqNm4zcVphQi1XX1Z2MXVtRTE1'}],
 'referredBy': '',
 'salesRep': {'id': 'VGpwQTRGTmw4MExVODl1b1BmXzBodTBwWnZXS2dUZzVvSkJKZUx4UlFpdzE1',
              'username': 'aarno.aukia'},
 'socialNetworks': [{'address': "'https://twitter.com/bashar_2018'",
                     'id': 'Y0c2YktIcG1kakt4RTJiRkh3NVVnYzNqejdkUkVrQVRkUE0tUVQ3TUpPdzE1',
                     'type': 'Twitter',
                     'typeId': 'ZGRlMHpBaXY3M05YUGc4a0pIY3lRdUFKN1JYaDd2VEphbzhSRkdzM2x4bzE1'}],
 'status': {'id': 'UE9zMy1abnhnNUJQWnVORE5BQzNicUFWQ3huLXF2eGlSdlIyYVFmVXh4UTE1',
            'name': 'Employee'},
 'subscribed': True,
 'tags': [{'id': 'Y0Y4VFRhbDZSZFl2eENuYWU4M2s4Q3FsNjExTk5ldjdVOFdWU29ZRy1UTTE1',
           'name': 'new tag',
           'score': 1}],
 'temperature': {'id': 'UTI0Nm14TlB4SmRkdVNLMjNWQWgwR2R2TjhySE1US1RtVEQ0T24tRWtFbzE1',
                 'name': 'Hot'},
 'timezone': 'W. Europe Standard Time',
 'title': 'Hawar1',
 'website': [{'id': 'MW5tUm5IcVVDYmhVZ0lSVndJenBxbDZra1ZwVEcxQXBVWDB6NkVCUWNRODE1',
              'websiteUrl': 'http://002.powercoders.org/students/bashar-said/index.html'},
             {'id': 'eG91X0tVcWU2a1A3dVg1b2JKQ1MyWGwzaGFjX1Q5RGRSNng3OE9XbGxBNDE1',
              'websiteUrl': 'http://002.powercoders.org/students/alan-omar/index.html'}]}


Profile updated
-----------------

**For example, we want to update the addresses in the previous profile**

.. code::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.update('TmpmT0QyUGE3UGdGejZMay1xbDNyUHJFWU91M2VwN0hCdGtZZFFCaWRZczE1', {
        "firstName": "Hawar",
        "lastName": "Afrin",
        "title": "Hawar1",
        "company": "HAWAR",
        "emails": [
            {
                "address": "bashar.said.2018@gmail.com",
                "type": "work",
            }
        ],
        "phones": [
            {
                "number": "0041 76 803 77 34",
                "type": "work",
            }
        ],
        "status": {
            "name": "Employee",
        },
        "temperature": {
            "name": "Hot",
        },
        "addresses": [
            {
             	"street": "Neugasse 10",
                "city": "Zürich",
                "state": "ZH",
                "zip": "8005",
                "country": "Switzerland",
                "type": "work",
            }
        ],
        #"subscribed": true,
        "timezone": "W. Europe Standard Time",
        "socialNetworks": [
            {
                "address": "'https://twitter.com/bashar_2018'",
                "type": "Twitter",
            }
        ],
    }
    )
    pp.pprint(profile)


output
-------
.. code::

    'addresses': [{'city': 'Zürich',
                'country': 'Switzerland',
    			'countryId': 'QmJzeldzQ25rbXluZGc4RzlDYmFmYlZOY2xTemMwX2ZoMll5UTJPenhsNDE1',
    			'id': 'OEFPUzJBeTdaWlVhU3FDR194dEk3NU8xTThxakZuQXV4aE9obHM3SVdKTTE1',
    			'state': 'ZH',
    			'street': 'Neugasse 10',
    			'type': 'Work',
    			'typeId': 'SjFENlU0Y2s2RDFpM0NKWEExRmVvSjZ4T3NJMG5pLWNYZjRseDBSaTVfVTE1',
    			'zip': '8005'}],


Add address to profile
------------------------

.. code::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.profile_add_address({
    "contactId": "TmpmT0QyUGE3UGdGejZMay1xbDNyUHJFWU91M2VwN0hCdGtZZFFCaWRZczE1"},
    {'street':"Langäcker 13",
     'zip_code':"5430",
     'city':"Wettingen",
     'country':"Switzerland"},
    "Home"
    )
    pp.pprint(profile)


output
---------
.. code::

    {'addresses': [{'city': 'Wettingen',
                'country': 'Switzerland',
                'countryId': 'QmJzeldzQ25rbXluZGc4RzlDYmFmYlZOY2xTemMwX2ZoMll5UTJPenhsNDE1',
                'id': 'eDZNV2d4Q1ZIR09UN2p1UlhzclVCdTM0LU81UW5TZzZmU05vLUtuVzdoMDE1',
                'state': '',
                'street': 'Langäcker 13',
                'type': 'Home',
                'typeId': 'M1ZkLXI3UnJqUWxUVDNFZUZ3MW5MdG5KSGZuN0lVemNDcXNLdzgzbjBDVTE1',
                'zip': '5430'},


               {'city': 'Zürich',
                'country': 'Switzerland',
                'countryId': 'QmJzeldzQ25rbXluZGc4RzlDYmFmYlZOY2xTemMwX2ZoMll5UTJPenhsNDE1',
                'id': 'OEFPUzJBeTdaWlVhU3FDR194dEk3NU8xTThxakZuQXV4aE9obHM3SVdKTTE1',
                'state': 'ZH',
                'street': 'Neugasse 10',
                'type': 'Work',
                'typeId': 'SjFENlU0Y2s2RDFpM0NKWEExRmVvSjZ4T3NJMG5pLWNYZjRseDBSaTVfVTE1',
                'zip': '8005'}

profile contains
------------------
.. code::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.profile_contains({
    "contactId": "QmJzeldzQ25rbXluZGc4RzlDYmFmYlZOY2xTemMwX2ZoMll5UTJPenhsNDE1",
    "firstName": "Hawar",
    "lastName": "Afrin",
    "title": "Hawar1",
    "company": "HAWAR",
    "emails": [
      {
        "address": "bashar.said.2018@gmail.com",
        "type": "work",
      }
    ],
    "addresses": [
            {
                "street": "Neugasse 10",
                "city": "Zürich",
                "state": "ZH",
                "zip": "8005",
                "country": "Switzerland",
                "type": "work",
            }
        ],
    "phones": [
            {
                "number": "0041 76 803 77 34",
                "type": "work",
            }
        ]


  }, "phones", "number", "0041 76 803 77 34")

    pp.pprint(profile)



output
-------
.. code::

    2018-03-13 09:21:23,556 - root - DEBUG - loading config file: aarno.yaml
    2018-03-13 09:21:23,559 - root - DEBUG - loaded config: {'app_key': ' ', 'app_secret': ' ',
    'hatchbuck_key': ' ', 'hatchbuck_source_xing': ' ', 'hatchbuck_source_linkedin': ' ',
    'hatchbuck_source_carddav': ' ', 'hatchbuck_tag_xing': 'Xing-aarno', 'hatchbuck_tag_linkedin': 'LinkedIn-aarno',
    'hatchbuck_tag_carddav': 'Adressbuch-aarno', 'user_key': ' ', 'user_secret': ' ', 'carddav_path':         'carddav/360afdfd542ea44f/'}

    True


Add a profile
---------------
.. code::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.profile_add("emails", "address", "baschar.said@hotmail.com", {'type': 'Home'})
    pp.pprint(profile)


output
-------
.. code::

 {'addresses': [],
 'campaigns': [],
 'contactId': 'cFk2SXB1emNXWFFuRGRPWnNCeGsyRUZ1NmxCeVdFZlJkV3lzdWVKN0dpZzE1',
 'customFields': [{'name': 'Comments', 'type': 'MText', 'value': ''},
                  {'name': 'Invoiced', 'type': 'Number', 'value': ''},
                  {'name': 'Language', 'type': 'Text', 'value': ''},
                  {'name': 'working at company since',
                   'type': 'Text',
                   'value': ''},
                  {'name': 'company size', 'type': 'Text', 'value': ''},
                  {'name': 'Birthday', 'type': 'Date', 'value': ''}],
 'emails': [{'address': 'baschar.said@hotmail.com',
             'id': 'SVJhdUZDUjZNcllHYVRnZW5XWVZub1kzYmdIRTNkUmpwbUllYlJPNkxKazE1',
             'type': 'Work',
             'typeId': 'VmhlQU1pZVJSUFFJSjZfMHRmT1laUmwtT0FMNW9hbnBuZHd2Q1JTdE0tYzE1'}],
 'firstName': '',
 'instantMessaging': [],
 'lastName': '',
 'phones': [],
 'referredBy': '',
 'salesRep': {'id': 'VGpwQTRGTmw4MExVODl1b1BmXzBodTBwWnZXS2dUZzVvSkJKZUx4UlFpdzE1',
              'username': 'aarno.aukia'},
 'socialNetworks': [],
 'status': {'id': 'UHQ4aTZUTXh2aDROQ0w0Z2dOSDlGM2ZkaXFRelhTLTJEVHNKWU02TXJ1bzE1',
            'name': 'Customer Opportunity'},
 'subscribed': True,
 'tags': [],
 'timezone': 'W. Europe Standard Time',
 'website': []}


Add tags
----------
.. code::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile =hatchbuck.add_tag('TmpmT0QyUGE3UGdGejZMay1xbDNyUHJFWU91M2VwN0hCdGtZZFFCaWRZczE1', 'new tag')
    pp.pprint(profile)


output
--------
.. code::

    2018-03-13 09:55:51,514 - root - DEBUG - starting with arguments: Namespace(config='aarno.yaml', noop=False,     verbose=True)
    2018-03-13 09:55:51,514 - root - DEBUG - loading config file: aarno.yaml
    2018-03-13 09:55:51,517 - root - DEBUG - loaded config: {'app_key': ' ', 'app_secret': ' ', 'hatchbuck_key': ' ',     'hatchbuck_source_xing': ' ',
    'hatchbuck_source_linkedin': ' ', 'hatchbuck_source_carddav': ' ', 'hatchbuck_tag_xing': 'Xing-aarno',     'hatchbuck_tag_linkedin': 'LinkedIn-aarno',
    'hatchbuck_tag_carddav': 'Adressbuch-aarno', 'user_key': ' ', 'user_secret': ' ', 'carddav_path': 'carddav/360afdfd542ea44f/'}

    2018-03-13 09:55:51,517 - hatchbuck - DEBUG - adding tag new tag to contact     TmpmT0QyUGE3UGdGejZMay1xbDNyUHJFWU91M2VwN0hCdGtZZFFCaWRZczE1
    2018-03-13 09:55:51,533 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTPS connection (1):     api.hatchbuck.com
    2018-03-13 09:55:52,216 - requests.packages.urllib3.connectionpool - DEBUG - "POST     /api/v1/contact/TmpmT0QyUGE3UGdGejZMay1xbDNyUHJFWU91M2VwN0hCdGtZZFFCaWRZczE1/Tags?api_key= '' HTTP/1.1" 201 14

**2018-03-13 09:55:52,220 - hatchbuck - DEBUG - success: "Tag(s) added"**


**Notice**:  the addition of a tag when viewing the profile
.. code::

    'tags': [{'id': 'Y0Y4VFRhbDZSZFl2eENuYWU4M2s4Q3FsNjExTk5ldjdVOFdWU29ZRy1UTTE1',
           'name': 'new tag',
           'score': 1}],


Add birthday to profile
--------------------------

.. code::

    from hatchbuck import Hatchbuck
    import pprint
    pp = pprint.PrettyPrinter()
    hatchbuck = Hatchbuck('NINIGkhjhg348gssdh2uh2hf6gsjd...')
    profile = hatchbuck.profile_add_birthday({
    "contactId": "TmpmT0QyUGE3UGdGejZMay1xbDNyUHJFWU91M2VwN0hCdGtZZFFCaWRZczE1"},
    {'month': '1', 'day': '1', 'year': '1984'})
    pp.pprint(profile)


output
-------
.. code::

    'customFields': [{'name': 'Comments', 'type': 'MText', 'value': ''},
                 {'name': 'Invoiced', 'type': 'Number', 'value': ''},
                 {'name': 'Language', 'type': 'Text', 'value': ''},
                 {'name': 'working at company since',
                   'type': 'Text',
                   'value': ''},
                 {'name': 'company size', 'type': 'Text', 'value': ''},
                 {'name': 'Birthday', 'type': 'Date', 'value': '1/1/1984'}],

