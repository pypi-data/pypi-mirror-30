# astroSQL - Database Tools for Astronomers
_Currently in development usable only by Filipenko Group._

Simple Python API and shell commands to access to existing astronomical MySQL database.

## Features
* **astroSQL** Python API:
    - [x] read SQL database
    - [x] update SQL database
    - [x] SQL query using peewee ORM
* **astroSQL** Shell Command
    - [ ]  query SQL database to text-based file
    - [ ]  update SQL database with text-based file

## Dependencies
* MySQL server
* Python 3.x
* Pypi

## Setup

1. Clone the project and pip install

    ```sh
    $ git clone https://github.com/ketozhang/astroSQL
    $ cd astroSQL
    $ pip install .
    ```

2. Edit the configuration file `config.yml` which is located in where pip installed this package `/path/to/site-package/`. You may also use short python method to do this:

    ```bash
    $ ls $(python -c "import site; print(site.getsitepackages()[0])")/astrosql
    ```

    In `config.yml` edit as necessary

    ```yml
    # Uncomment 'forward' if you want to place config.yml elsewhere, specify the file path (maybe `~/.astrosql/config.yml` ?)
    # forward: '/path/to/config.yml'

    # Comment out any unecessary lines, empty will be read
    mysql:
        host: 'localhost'
        user: 'username'
        password: ''
        database: 'database_name'
    ```

    > <span style="color:rgb(200,0,0)">WARNING:</span> Keep this file secure if password is written

## Usage

See [wiki](https://github.com/ketozhang/astroSQL/wiki):

* [Python Usage](https://github.com/ketozhang/astroSQL/wiki/Python-Usage)
* [Shell Usage](https://github.com/ketozhang/astroSQL/wiki/Shell-Usage)

## References
**Filippenko Group - Project Team**
The program was built for the Filippenko Group, astronomy researchers led by [Alex Filippenko](https://astro.berkeley.edu/faculty-profile/alex-filippenko) for analyzing data from the Lick Observatory and Keck Observatory.

Project team led by [Thomas Jaeger](https://astro.berkeley.edu/researcher-profile/3420275-thomas-de-jaeger), [Keto Zhang](https://github.com/ketozhang), and [Weikang Zheng](https://astro.berkeley.edu/researcher-profile/2358133-weikang-zheng).

**Source Code and Inspiration**:
Some parts of the program was provided by and inspired from [Issac Shiver](https://github.com/ishivvers) and [Thomas Tu](https://github.com/thomastu) from [FlipperPhoto repo](https://github.com/ketozhang/FlipperPhoto/tree/master/flipp/libs).
