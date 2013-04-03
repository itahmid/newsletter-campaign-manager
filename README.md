pipmail
=======

Email campaign manager written using the Python Flask micro-framework.  Adapting my pymail project for a specific application.

todo
=======
- add models/use ORM for database lookups ~~(maybe)~~ (probably)
- add everything the old Ruby/PHP versions have
- add an error_dict for checking edit_recipient form contents
- edit sql column list_id for recipients to accept multiple list_ids
- add section for assinging lists to campaigns
- email templates and delivery
- statistics
- campaign searches
- types/companies/staff
- unsubscribe links/unsubscriber search & deletion

installation
=======
- sudo pip install virtualenv
- cd /pipmail
- virtualenv venv
- . venv/bin/activate
- pip install Flask

Then edit the settings.py.change and rename it to settings.py and run the runserver.py file.
