import datetime

def format_date(value, format='%a, %d %b %Y'):
    return value.strftime(format)

def format_value(value):
    if isinstance(value, str) or isinstance(value, int):
        # Don't need to do anything special for strings/ints
        return value
    elif isinstance(value, list):
        # Convert the list to a print format.
        return ', '.join(value)
    elif isinstance(value, datetime.datetime):
        # Use the nice date formatter for dates
        return format_date(value)
    else:
        # Just convert the value to a string if we get any other type.
        return str(value)
