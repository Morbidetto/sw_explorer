This Django application can download characters info from SWAPI, store them in CSV files and display them.
It was wrriten with assumption that SWAPI db can be much larget than it is today and with possibility to add others similiar apps like vehicles dataset easily

#### Stack
* Python 3.10
* Django 4.0
* petl 1.7
* PostgreSQL 14

### Start
First make sure that you have docker-compose properly installed and configured.
Appplication is dockerized and contains self-hosted SWAPI instance as a git-submodule. Please run:
* `git submodule init`
* `git submodule update`
* Now you need to aply Django migrations `make migrate`
* You can now launch application by '`make start`
* Go to http://127.0.0.1:8000/ to explore the app and click on Characters module.
* To run tests run `make tests`
* If you want to use another SWAPI instance then edit `SWAPI_URL` setting

### To do
* FE could use some love, like proper React app.
* Characters templates could be more general so they could be used in other apps as well
* Pagination should be added to CharactersDetailView for large files and large row limit to prevent user from loading entire file to memory.
* Production docker-compose should be created which would use uWSGI/gunicorn and nginx instead of Django server
* Tests for file operations
* Add queue and task system for downloading data
