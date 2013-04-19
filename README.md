pipmail
=======

Email campaign manager written using the Python Flask micro-framework.  Adapting my pymail project for a specific application.

todo
=======
- fix recipient adding view
- add everything the old Ruby/PHP versions have
- tests
- add an error_dict for checking edit_recipient form contents
- edit sql column list_id for recipients to accept multiple list_ids
- add section for assinging lists to campaigns and fix steps process
- email templates and delivery
- statistics
- campaign searches
- types/companies/staff
- multiple list ids for campaigns
- unsubscribe links/unsubscriber search & deletion

installation
=======
- sudo pip install virtualenv
- cd /pipmail
- virtualenv venv
- . venv/bin/activate
- pip install Flask

Then edit the settings.py.change and rename it to settings.py and run the runserver.py file.
