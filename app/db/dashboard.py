from typing import Union

import pandas as pd
import pygsheets as pg

from app.config.setting import settings as s


class GCClient:
    def __init__(self):
        self.gc_client = pg.authorize(service_file=s.gc_config_path)

    def get_ws(self, name: str, url: str = s.dashboard_url, to_type: str = "df") -> Union[pg.Worksheet, pd.DataFrame]:
        ws = self.gc_client.open_by_url(url)
        sheet_names = [i.title for i in ws.worksheets()]

        if to_type == "df":
            if name not in sheet_names:
                return pd.DataFrame()
            else:
                return ws.worksheet_by_title(name).get_as_df()
        elif to_type == "ws":
            if name not in sheet_names:
                return None
            return ws.worksheet_by_title(name)
        else:
            raise ValueError(f"Invalid type `{to_type}` provided. Valid types are `df` and `ws`.")
