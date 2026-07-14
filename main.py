import os
import sys
import traceback
import logging
import nextcord
import atexit

from managers.lifecycle import close_all
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from nextcord.ext import commands

Debug = True
logging.getLogger("lavalink.transport").setLevel(logging.ERROR)
logging.getLogger("lavalink.nodemanager").setLevel(logging.ERROR)
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)
commands_path = ["commands/impl", "events"]
initial_extensions = []

def resolve_extension_name(cog_name):
    if "." in cog_name:
        return cog_name
    base_dir = os.path.dirname(os.path.realpath(__file__))
    for path in commands_path:
        full_path = os.path.join(base_dir, os.path.normpath(path), f"{cog_name}.py")
        if os.path.exists(full_path):
            return f"{path.replace('/', '.')}.{cog_name}"
    return cog_name

# 這裡建個指令讓你可以載入Cog
@bot.command()
async def load(ctx, cog_name):
    try:
        bot.load_extension(resolve_extension_name(cog_name))
    except:
        await ctx.send('Failed.')
        return
    await ctx.send('load success!')

# 這裡建個指令讓你可以卸載Cog
@bot.command()
async def unload(ctx, cog_name):
    try:
        bot.unload_extension(resolve_extension_name(cog_name))
    except:
        await ctx.send('Failed.')
        return
    await ctx.send('unload success!')

# 這裡建個指令讓你可以重新載入Cog
@bot.command()
async def reload(ctx, cog_name):
    try:
        bot.reload_extension(resolve_extension_name(cog_name))
    except:
        await ctx.send('Failed.')
        return
    await ctx.send('reload success!')
    
# 載入Cog
def load_cogs(base_dir):
    initial_extensions.clear()
    for path in commands_path:
        full_path = os.path.join(base_dir, os.path.normpath(path))
        for filename in os.listdir(full_path):
            if filename.endswith('.py') and not filename.startswith("_"):
                extension = f"{path.replace('/', '.')}.{filename[:-3]}"
                initial_extensions.append(extension)
    
# 主程式進入點
def main():
    try:
        base_dir = os.path.dirname(os.path.realpath(__file__)) # 取得目前檔案的路徑
        load_cogs(base_dir)
        for extension in initial_extensions:
            bot.load_extension(extension)
                
        atexit.register(close_all)
        bot.run(os.environ.get("BOT_TOKEN"))
                
    except Exception as e:
        error_class = e.__class__.__name__
        detail = e.args[0]
        cl, exe, tb = sys.exc_info()
        lastCallStack = traceback.extract_tb(tb)[-1]
        fileName = lastCallStack[0]
        lineNum = lastCallStack[1]
        funcName = lastCallStack[2]
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(
            fileName, lineNum, funcName, error_class, detail)
        print(errMsg)

if __name__ == "__main__":
    main()
