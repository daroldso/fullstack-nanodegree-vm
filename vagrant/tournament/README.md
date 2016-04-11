Tournament Planner
=============
This is the Project 2 of Full Stack Web Developer Nanodegree by Udacity

## Installation
To test this project, clone this project and go into `vagrant` folder. Run 
```
vagrant up
``````
After virtual machine is up and running, run
```
vagrant ssh
``````
After entering the virtual machine, `cd` into `/vagrant/tournament` folder

## Database
To initialize the database, run
```
psql
``````
and then 
``````
\i tournament.sql
```

## Test
After initializing the database, run
``````
python tournament_test.py
```