Item Catalog
=============
This is the Project 3 of Full Stack Web Developer Nanodegree by Udacity. I used "Genre" as category and "Artist" as item.

## Installation
To test this project, clone this project and go into `vagrant` folder. Run 
```
vagrant up
``````
After virtual machine is up and running, run
```
vagrant ssh
``````
After entering the virtual machine, `cd` into `/vagrant/catalog` folder

## Database
To initialize the database, run
```
python database_setup.py
``````
and then add some default data to database by
``````
python add_fixture.py
```

## Running the web server to serve the application
After initializing the database and adding data, run
``````
python main.py
```
Navigate to `http://localhost:8000` and you are good to go!

## JSON Endpoints
There are 3 json endpoints to retrieve genres and artists in json data format.

Get all genres with all artists under it
```
http://localhost:8000/genres.json
```
Get all artists
```
http://localhost:8000/artists.json
```
Get specific artist
```
http://localhost:8000/artists/:artist_id/json
```