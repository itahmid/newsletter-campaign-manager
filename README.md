pipmail
=======

Email campaign manager written using the Python Flask micro-framework.  Adapting my pymail project for a specific application.

todo
=======
- ~~add models/use ORM for database lookups~~  ~~(maybe)~~ ~~(probably)~~ my class models are better
- add everything the old Ruby/PHP versions have
- email templates and delivery
- statistics/reporting page like in old pipmail
- campaign searches
- types/companies/staff
- multiple list ids for campaigns
- unsubscribe links/unsubscriber search & deletion
- add tests
- more robust error handling
- fix table macros/pagination

installation
=======
- sudo pip install virtualenv
- cd /pipmail
- virtualenv venv
- . venv/bin/activate
- pip install Flask

Then edit the settings.py.change and rename it to settings.py and run the runserver.py file.
