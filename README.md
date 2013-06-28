pipmail
=======

Email campaign manager written using the Python Flask micro-framework.  Adapting my pymail project for a specific application.

todo
=======
- add everything the old PHP version has
- add templates/daily update/sections/articles/delivery
- statistics/reporting page like in old pipmail
- campaign searches
- types/companies/staff
- unsubscribe links/unsubscriber search & deletion
- add tests
- more robust error handling
- fix table macros/pagination
- fix styling of tables
- fix the campaign search styling
- create script to generate mysql tables from schema
- delete old unnecessary files

installation
=======
- sudo pip install virtualenv
- cd /pipmail
- virtualenv venv
- . venv/bin/activate
- pip install Flask

Then edit the settings.py.change and rename it to settings.py and run the runserver.py file.
