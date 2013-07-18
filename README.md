pipmail
=======

An email campaign manager written using the Python Flask micro-framework and Twitter Bootstrap.

todo
=======
- fix the pagination on index pages (get the # of items first)
- add articles/sections from old pipmail
- edit the message content step
- statistics/reporting page like in old pipmail
- campaign searches
- types/companies/staff
- fix the checkbox for the unsubscriber link in newsletter creation
- add tests
- more robust error handling
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
