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
    version                     = "0.2.1",
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

*Lets assume we have a database with a user table that can be fetched with this query:*

::
  
      SELECT id,
             first_name,
             last_name,
             email,
             age
        FROM users

Formatting
=============

*Here is how you could write a simple template to turn the SQL result (list of dicts) into a
 prettier JSON structure:*

::

    struct = {
        "< id": {
            "id": "< id",
            "name": {
                "first": "< first_name",
                "last": "< last_name",
                "full": "{{first_name}} {{last_name}}"
            },
            "email": "< email",
            "age": "< age"
        }
    }

    collection			= Restruct.collection( <list_of_dicts_from_database_query> )
    collection.format(struct)

    # Example output:
    {
        273667: {
            "id": 273667,
            "name": {
                "first": "Jeff",
                "last": "Goldbloom",
                "full": "Jeff Goldbloom"
            },
            "email": "jeff.goldbloom@example.com",
            "age": 49
        },
        93892: {
            "id": 93892,
            "name": {
                "first": "Marty",
                "last": "Mcfly",
                "full": "Marty Mcfly"
            },
            "email": "marty.mcfly@example.com",
            "age": 17
        },
        ...
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
