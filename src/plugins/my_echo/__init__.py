from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.plugin import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="my_echo",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

my_echo = on_command("echo", priority=10, block=True)

@my_echo.handle()
async def my_echo_handler(args: Message = CommandArg()):
    await my_echo.finish(args.extract_plain_text())