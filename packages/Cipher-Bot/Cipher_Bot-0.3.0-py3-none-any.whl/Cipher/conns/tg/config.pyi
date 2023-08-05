from typing import List

class TGConnectionConfig(ConnectionConfig):
    type: str
    channels: List[dict]
    token: str
