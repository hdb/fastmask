from fastmask import config

from typing import Any
from rich import print, box
from rich.table import Table
from rich.console import Console
from datetime import datetime
import pandas as pd

def error_msg(msg: str, exit_: bool = True) -> None:
    print(f'[red bold]{msg}')
    if exit_:
        print("[white]Exiting...\n")
        exit()

def success_msg(msg: str) -> None:
    print(f'[green]{msg}')

def try_get(k: str, src: dict, default=None) -> Any:
    return src[k] if k in src else default

def is_none(val) -> bool:
    return val is None or len(val) == 0

def to_date(d: str) -> datetime:
    return datetime.strptime(d, config.TIME_FORMAT)

def handle_output(r: list[dict], o: str, j: bool, t: str) -> None:

    column_order = [
        'email',
        'forDomain',
        'description',
        'state',
        'lastMessageAt',
        'url',
        'id',
        'createdAt',
        'createdBy',
    ]

    if o is not None:
        if o.lower().endswith('.csv'):
            pd.DataFrame(r).to_csv(o, index=False, columns=column_order)
        elif o.lower().endswith('.json'):
            pd.DataFrame(r).to_json(o, orient='records', indent=4)
        else:
            error_msg('Output is supported for json or csv format.')
    elif j:
        print(pd.DataFrame(r).to_json(orient='records', indent=4))
    else:
        PrettyTable(r, title=t).out()

class PrettyTable():

    def __init__(self, data_: list[dict], title: str | None = None):
        self.table = Table(title=title, box=box.MINIMAL, header_style='italic')
        self.generate_cols()
        self.generate_rows(data_)

    @staticmethod
    def compute_style(datum: str, ref: dict) -> str:
        style = try_get(
            datum,
            try_get(
                'row_style',
                ref,
                {}
            ),
            ''
        )
        return f'[{style}]' if len(style) > 0 else style

    @staticmethod
    def compute_value(datum: Any, ref: dict) -> str:
        return try_get(
            'transform',
            ref,
            (lambda x: x.replace('[','\[') if x is not None else '') # escape brackets for Rich rendering
        )(datum)

    def generate_rows(self, data_: list[dict]) -> None:
        for x in data_:
            row = []
            for k,v in config.table_schema.items():
                if not try_get('hide',v,False):
                    style = self.compute_style(x[k], v)
                    value = self.compute_value(x[k], v)
                    row.append(style + value)
            self.table.add_row(*row)

    def generate_cols(self) -> None:
        for k,v in config.table_schema.items():
            if not try_get('hide',v,False):
                self.table.add_column(try_get('header',v,k), style=try_get('style',v), no_wrap=True)

    def out(self) -> None:
        console = Console()
        print()
        console.print(self.table)
