from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from factory_alchemist.generators import _generate_value, add_type


BaseModel = None


def make(session, model_, **kwargs):
    if isinstance(model_, Table):
        table = model_
        model_ = type('', (declarative_base(),), {'__table__': table})

    record = model_(**kwargs)

    for column in _non_nullable_columns(*model_.__table__.columns.values()):
        if column.name in kwargs:
            continue  # field already filled
        elif column.foreign_keys:
            for foreign_key in column.foreign_keys:
                fk_value = make(session, _get_class_by_tablename(foreign_key.column.table.name))
                setattr(record, foreign_key.parent.name, getattr(fk_value, foreign_key.column.name))
        else:
            default_value = column.default.execute() if column.default else None
            setattr(record, column.name, default_value or _generate_value(column.type))

    session.add(record)
    session.flush()
    return record


def make_t(table_, **kwargs):
    record_values = {column.name: None for column in table_.columns}

    for column in _non_nullable_columns(*table_.columns):
        if column.name in kwargs:
            continue

        if column.foreign_keys:
            for foreign_key in column.foreign_keys:
                fk_value = make_t(foreign_key.column.table)
                record_values[column.name] = getattr(fk_value, foreign_key.column.name)
        else:
            record_values[column.name] = _generate_value(column.type)

    record_values.update(kwargs)

    result = table_.insert().values(**record_values).execute()

    # assume this table has exactly one primary key
    key_name = table_.primary_key.columns.keys()[0]
    key_value = result.lastrowid

    return table_.select(getattr(table_.c, key_name) == key_value).execute().first()


def _non_nullable_columns(*columns):
    return {column for column in columns
            if not column.nullable and not column.primary_key}


def _get_class_by_tablename(tablename):
  if not BaseModel:
      raise Exception('BaseModel must be defined')

  for c in BaseModel._decl_class_registry.values():
    if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
      return c
