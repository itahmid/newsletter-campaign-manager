pipmail
=======

Email campaign manager written using the Python Flask micro-framework.  Adapting my pymail project for a specific application.

todo
=======
- add everything the old Ruby/PHP versions have
- finish new models/inheritance
- edit subscribers view for non-step list adding
- edit sql column list_id for recipients to accept multiple list_ids
- add section for assinging lists to campaigns and fix steps process
- email templates and delivery
- statistics/reporting page like in old pipmail
- campaign searches
- types/companies/staff
- multiple list ids for campaigns
- unsubscribe links/unsubscriber search & deletion
- probably read more about context processors and maybe redo the authentication process
- add tests
- more robust error handling

installation
=======
- sudo pip install virtualenv
- cd /pipmail
- virtualenv venv
- . venv/bin/activate
- pip install Flask

Then edit the settings.py.change and rename it to settings.py and run the runserver.py file.
