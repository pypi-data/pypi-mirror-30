import string
import random
from datetime import date, datetime
from sqlalchemy import SmallInteger, Integer, BigInteger, Float, String, CHAR, Boolean, Date, DateTime, Enum


try:
    lowercase_chars = string.ascii_uppercase
except AttributeError:
    lowercase_chars = string.lowercase


def _generate_value(type_):
    value_generator = TYPE_VALUE_GENERATOR_MAPPER.get(type_.__class__)

    if value_generator:
        return value_generator(type_)


def rand_word(length):
   return ''.join(random.choice(lowercase_chars) for i in range(length))


def generate_int(type_=None, max=2147483647):
    return random.randint(0, max)


def generate_smallint(type_=None):
    return generate_int(type_, 1)


def generate_bigint(type_=None):
    return generate_int(type_, 9223372036854775807)


def generate_float(type_=None):
    return random.uniform(0.0, 99999.0)


def generate_str(type_=None):
    length = type_.length if type_.length else 50
    return rand_word(length)


def generate_bool(type_=None):
    return random.choice((True, False))


def generate_date(type_=None):
    return date(random.randint(1950, 2050), random.randint(1, 12), random.randint(1, 28))


def generate_datetime(type_=None):
    return datetime(random.randint(1950, 2050), random.randint(1, 12), random.randint(1, 28),
                    random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))


def generate_enum(type_=None):
    return random.choice(type_.enums)


def add_type(type_, value_generator):
    TYPE_VALUE_GENERATOR_MAPPER[type_] = value_generator


TYPE_VALUE_GENERATOR_MAPPER = {
    SmallInteger: generate_smallint,
    Integer: generate_int,
    BigInteger: generate_bigint,
    Float: generate_float,
    String: generate_str,
    CHAR: generate_str,
    Boolean: generate_bool,
    Date: generate_date,
    DateTime: generate_datetime,
    Enum: generate_enum,
}