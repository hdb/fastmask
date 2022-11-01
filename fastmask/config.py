from datetime import datetime

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def to_date(d: str) -> datetime:
    return datetime.strptime(d, TIME_FORMAT)

table_schema = {
    'description': {
        'header': 'Description',
        'style': 'blue',
        'transform': (lambda x: x if x != '' else 'n/a'),
        'row_style': {
            '': 'dim',
        }
    },
    'email': {
        'header': 'Email',
        'style': 'cyan',
    },
    'id': {
        'header': 'ID',
    },
    'createdAt': {
        'header': 'Created',
        'style': 'italic',
        'transform': (lambda x: datetime.strftime(to_date(x), '%m/%d/%y'))
    },
    'lastMessageAt': {
        'header': 'Last Msg',
        'style': 'italic',
        'row_style': {
            None: 'dim',
        },
        'transform': (lambda x: datetime.strftime(to_date(x), '%m/%d/%y') if x is not None else
        'Never')
    },
    'state': {
        'header': 'State',
        'row_style': {
            'enabled': 'green',
            'disabled': 'red',
            'deleted': 'dim',
            'pending': 'yellow',
        }
    },
    'forDomain': {
        'header': 'Domain',
        'style': 'cyan bold',
        'hide': True,
    },
    'url': {
        'header': 'URL',
        'style': 'cyan',
    },
    'createdBy': {
        'header': 'By',
        'style': 'yellow',
        'transform': (lambda x: x[11:]),
        'hide': True
    },
}
