from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.plugin import on_command
from nonebot.adapters import Message
from nonebot.adapters import Event
from nonebot.params import CommandArg

from .config import Config

import requests
import json
from datetime import date
import hashlib
from typing import List, Optional, Tuple
from pathlib import Path

__plugin_meta__ = PluginMetadata(
    name="Fortune",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


fortune = on_command("今日人品", aliases={"jrrp"}, priority=5, block=True)


def date_hash(X: str, mod):
    today = date.today()
    date_str = today.strftime("%Y%m%d")
    combined_str = X + date_str
    
    hash_object = hashlib.sha256(combined_str.encode())
    hash_hex = hash_object.hexdigest()
    hash_value = sum(int(hash_hex[i:i+2], 16) for i in range(0, len(hash_hex), 2))
    
    return hash_value % mod


def get_copywriting(id: str) -> Tuple[str, str]:
    _p: Path = Path.cwd() / "src/plugins/fortune" / "resource/copywriting.json"

    with open(_p, "r", encoding="utf-8") as f:
        content = json.load(f).get("copywriting")
        luck = content[date_hash(id, 19)]
        title: str = luck.get("good-luck")
        list_len = len(luck.get("content"))
        text: str = (luck.get("content"))[date_hash(id + id, list_len)]

        return title, text


@fortune.handle()
async def fortune_handler(event: Event):
    user_id = event.get_user_id()
    copywriting = get_copywriting(user_id)
    await fortune.finish("\n✨今日人品✨\n" + "【运势】：" + copywriting[0] + "\n【签语】：" + copywriting[1], at_sender=True)
