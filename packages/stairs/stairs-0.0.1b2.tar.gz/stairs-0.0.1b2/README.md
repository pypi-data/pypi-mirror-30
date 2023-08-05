# Stairs

Context-based DB/Transaction/Session manager for SQLAlchemy

Can it be used in your project?
[![Build Status](https://travis-ci.org/tgrx/stairs.svg?branch=master)](https://travis-ci.org/tgrx/stairs)

## Install

```bash
pip install stairs
```

## Example

```python

import sqlalchemy as sa

import stairs

stairs.configure('postgresql://user:password@dbhost:5432/dbname')


with stairs.Transaction() as t:
    # -------------------------------------------
    # example of ORM setup
    # feel free to keep to your favorite approach
    from sqlalchemy.ext.automap import automap_base
    Base = automap_base()
    Base.prepare(t.engine, reflect=True)
    User = Base.classes.user
    # -------------------------------------------

    new_user = User(email='your@email.test')
    t.session.add(new_user)
    t.session.flush()
    
    query = sa.update(User).values({User.name: 'dev'})
    t.session.execute(query)
    
    # t.rollback() or t.session.rollback() will exit context
    
# data are committed here, on context exit
```
