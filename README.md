# ticketmaestro
technical test for JP morgan

To test it, you need to install  django_nose

You cannot use an SQLite database because, SQLite concurency model doesn't allow to work on multiple thread which the app does.
I used MySQL, but any other db should work, just update settings.py to match the db your are using.
And of course install the python module needed to work with this particular database

Most of the code you will be interested in is located in booking/booking.py

