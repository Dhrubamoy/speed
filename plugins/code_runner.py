# Copyright (C) 2020-2021 by TeamSpeedo@Github, < https://github.com/TeamSpeedo >.
#
# This file is part of < https://github.com/TeamSpeedo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamSpeedo/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import io
import sys
import traceback

import requests

from database.sudodb import is_user_sudo, sudo_list, add_sudo, rm_sudo
from main_start.core.decorators import speedo_on_cmd
from main_start.core.startup_helpers import run_cmd
from main_start.helper_func.basic_helpers import (
    edit_or_reply,
    edit_or_send_as_file,
    get_text,
)
from main_start.helper_func.basic_helpers import (
    edit_or_reply,
    edit_or_send_as_file,
    get_text,
    get_user,
    iter_chats,
)
@speedo_on_cmd(
    cmd=["exec", "eval"],
    ignore_errors=True,
    cmd_help={"help": "Run Python Code!", "example": '{ch}eval print("FridayUserBot")'},
)
async def eval(client, message):
    engine = message.Engine
    ngine = message.Engine
    msg_ = await edit_or_reply(message, engine.get_string("PROCESSING"))
    text_ = get_text(message)
    stark = await edit_or_reply(message, engine.get_string("PROCESSING"))
    cmd = get_text(message)
    user = get_user(message, text_)[0]
    if await is_user_sudo(user.id):
      return await stark.edit(engine.get_string("Sorry! It is sudo restricted command due to security reasons").format(user.mention))
    if not cmd:
        await stark.edit(engine.get_string("INPUT_REQ").format("Python Code"))
        return
    if message.reply_to_message:
        message.reply_to_message.message_id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success!"
    EVAL = engine.get_string("EVAL")
    final_output = EVAL.format(cmd, evaluation)
    capt = "Eval Result!" if len(cmd) >= 1023 else cmd
    await edit_or_send_as_file(final_output, stark, client, capt, "eval-result")


async def aexec(code, client, message):
    exec(
        f"async def __aexec(client, message): "
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)

@speedo_on_cmd(
    cmd=["bash", "terminal"],
    ignore_errors=True,
    cmd_help={"help": "Run Bash/Terminal Command!", "example": "{ch}bash ls"},
)
async def sed_terminal(client, message):
    engine = message.Engine
    ngine = message.Engine
    msg_ = await edit_or_reply(message, engine.get_string("PROCESSING"))
    text_ = get_text(message)
    stark = await edit_or_reply(message, engine.get_string("PROCESSING"))
    cmd = get_text(message)
    user = get_user(message, text_)[0]
    stark = await edit_or_reply(message, engine.get_string("WAIT"))
    if await is_user_sudo(user.id):
      return await stark.edit(engine.get_string("Sorry! It is sudo restricted command due to security reasons").format(user.mention))
    cmd = get_text(message)
    if not cmd:
        await stark.edit(engine.get_string("INPUT_REQ").format("Bash Code"))
        return
    cmd = message.text.split(None, 1)[1]
    if message.reply_to_message:
        message.reply_to_message.message_id

    pid, err, out, ret = await run_command(cmd)
    if not out:
        out = "No OutPut!"
    friday = engine.get_string("BASH_OUT").format(cmd, pid, err, out, ret)
    await edit_or_send_as_file(friday, stark, client, cmd, "bash-result")


async def run_command(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    errors = stderr.decode()
    if not errors:
        errors = "No Errors!"
    output = stdout.decode()
    return process.pid, errors, output, process.returncode
