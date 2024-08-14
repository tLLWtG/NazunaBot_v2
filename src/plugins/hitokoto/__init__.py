from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.plugin import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

from .config import Config

import requests
import json

__plugin_meta__ = PluginMetadata(
    name="Hitokoto",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

hitokoto = on_command("hitokoto", priority=5, block=True)

@hitokoto.handle()
async def hitokoto_handler(args: Message = CommandArg()):
    hitokoto_arg = args.extract_plain_text()
    res = await get_hitokoto()
    await hitokoto.send(res[0])
    if hitokoto_arg != '-h' and len(res) == 2:
        await hitokoto.send(f'from: {res[1]}')

async def get_hitokoto() -> list:
    try:
        res_text = requests.get('https://v1.hitokoto.cn/?c=a&c=b&c=d&c=i&c=k').text
    except:
        return ['与 Hitokoto 服务器通信异常 QAQ']
    
    try:
        res_dict = json.loads(res_text)
    except:
        return ['无法解析接收到的 Hitokoto 信息 QAQ']
    
    hitokoto_text = res_dict['hitokoto']
    hitokoto_from = res_dict['from']

    return [hitokoto_text, hitokoto_from]