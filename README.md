## Requirements
* [Python 3](https://www.python.org/downloads/) 
* [Django](https://www.djangoproject.com/download/) 
* Celery[v3.1.24]: `$ pip install celery==3.1.24`
* Redis
	* [For windows](https://github.com/MicrosoftArchive/redis/releases)
	* [Other](https://redis.io/download) 

## Usage
* Run `$ redis-server`
* Open another terminal in the project folder and run `$ python manage.py runserver`
* Open another terminal in the project folder and run `$ celery worker -A webproject --loglevel=debug --concurrency=4`
