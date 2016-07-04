# SOSGrader v2

A complete rewrite of the old SOS Camp 3 grader with Python 2/3 Java support.

![Screenshot](http://i.imgur.com/YybCLbg.png)

## Installation

The easiest way to setup is to use Docker Compose file.

```sh
sudo MYSQL_PASSWORD=hackme GRADER_SECRET=hackme \
     ADMIN_USERNAME=admin ADMIN_PASSWORD=hackme \
     GRADER_VERBOSE=true \
     docker-compose up
```

Other available variables:

- ADMIN_EMAIL
- ALLOWED_HOST

To make initial grading fast, you may want to download the images used:

``` sh
for i in java:jdk python:3-alpine python:2-alpine; do
sudo docker pull $i
done
```

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

## License

SOSGrader, online multilanguage judge system
Copyright (C) 2016 Manatsawin Hanmongkolchai

This program is free software: you can redistribute it and/or modify
it under the terms of the [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html) as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
