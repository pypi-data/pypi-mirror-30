from setuptools import setup

setup(
    name                        = "restruct",
    packages                    = [
        "restruct",
    ],
    package_dir                 = {
        "restruct":		".",
    },
    install_requires            = [
        'populater',
    ],
    version                     = "0.2.0",
    include_package_data        = True,
    author                      = "Matthew Brisebois",
    author_email                = "matthew@webheroes.ca",
    url                         = "https://github.com/webheroesinc/restruct",
    license                     = "Dual License; GPLv3 and Proprietary",
    description                 = "Turn SQL results into beautiful JSON structures",
    long_description		= """Restruct is an easy light-weight formatting library that simplifies the process of representing
SQL results in a human readable format (JSON).  Pass the restruct method your SQL results and a
formatting structure and voila, you have turned your complex SQL result into beautiful JSON.  One of
the best features of Restruct is squashing all the duplicate entries from SQL joins into a sub
section of your JSON structure.

===============
 Usage examples
===============

*Lets assume we have an SQL join for a 1 to 1 relationship and that all the format variables used
represent columns in the select tables.*

::
  
      SELECT user_id,
             user_level,
             level_name,
             first_name,
             last_name,
             email
        FROM users
        JOIN user_levels USING (user_level_id)

Formatting
=============

*An example format structure for results from the above query:*

::

    {
        ".single": true,
        ".key": "{user_id}",
        "id": ": {user_id}", 
        "level": {
            "id": ": {user_level}", 
            "name": ": {user_level_name}"
        },
        "name": {
            "first": ":< first_name",
            "last": ":< last_name", 
            "full": "{first_name} {last_name}"
        },
        "email": true
    }

    """,
    keywords                    = ["mysql", "sqlite", "sql", "json"],
    classifiers                 = [
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
    ],
)
