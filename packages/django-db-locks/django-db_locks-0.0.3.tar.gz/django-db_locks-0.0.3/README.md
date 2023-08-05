# django-db-locks
SQL database locking backend for processes

to install:
```
pip install django-db-locks
```

A db can be specified by adding the router to your DATABASE_ROUTERS and creating the locks 
setting dict:

```python
DATABASE_ROUTERS = [
    ...,
    locks.router.Router
]

LOCKS ={
    'db': 'mydb'
}
```
