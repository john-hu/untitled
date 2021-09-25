# Development env

* Python 3.9+
* SQLite DB (short-term)

## How to start the project

### Clone the repo:
```shell
git clone git@github.com:john-hu/untitled.git
```

### Initialize and activate env
If you use console/terminal to start the project, we may need to create a virtual env.
```shell
python -m virtualenv venv
```

If you use PyCharm to start the project, please add a virtual env interpreter named with venv.

After that, we should activate the virtual env with the followings:
* Windows PowerShell: `venv\Scripts\activate.psl`
* Mac/Linux: `source venv/bin/activate`

After all setup, you should find similar prefix in your console/terminal:

```shell
# mac/ubuntu
(venv) ~/git/untitled>
# windows powershell
(venv) PS C:\Users\hchu\git\untitled>
```

### Start the project

```shell
# initialize the database
python manage.py migrate
# start the dev server
python manage.py runserver
```

Open your browser with http://localhost:8000/ to see [the website](http://localhost:8000/).
