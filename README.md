# SOSGrader v2

A complete rewrite of the old SOS Camp 3 grader with Python 2/3 Java support.

![Screenshot](http://i.imgur.com/YybCLbg.png)

## Installation

The easiest way to setup is to use Docker Compose file.

## Components

This grader composes of 3 components:

- API Server written in Django with Django REST framework
- Grader runner written in Node.js
- Frontend written in AngularJS 1

The frontend is shipped as part of the API server, but is not required (you can
write your own frontend). In fact, all components are separated enough that you
can replace each parts (maybe using Grader v1's components).

## Changes from Grader v1

Grader v1 is stil available in the master branch. It has two interfaces, oldui
and frontend. In SOSGrader v2 oldui support is removed and replaced by Django
Admin interface.

- Problem write API is no longer supported.
- Parts of the API that was designed, but not implemented are removed
- Date format is changed to ISO8601 instead of POSIX time
- Many unused languages are removed.
- Java input generator support is removed
- Faster grader runner with direct API interaction, instead of using the `docker`
  command line.

### Migrating from v1

To migrate from v1:

1. Install the grader in a separated database
2. Copy the data from `tests` table from v1 to `problems_test`. The structure
   should be similar enough
3. Copy the `problems` table from v1 to the database
4. Run `python manage.py migratephp` to move code from BLOB to file.
