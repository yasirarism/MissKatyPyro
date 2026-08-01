# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import asyncio
import html
import privatebinapi

from cachetools import TTLCache
from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError
from pyrogram import enums, filters
from pyrogram.types import (
    InlineQueryResultArticle,
    InputRichMessage,
    InputTextMessageContent,
    LinkPreviewOptions,
    Message,
)


class _GuestInlineMessage:
    """Tiny adapter to mimic Message.edit_msg() for Guest Mode replies.

    Guest replies are *inline messages* and must be edited using edit_inline_text.
    """

    def __init__(self, client, inline_message_id: str):
        self._client = client
        self.inline_message_id = inline_message_id

    async def edit_msg(self, text: str, disable_web_page_preview: bool = None, **kwargs):
        link_preview_options = None
        if disable_web_page_preview is not None:
            link_preview_options = LinkPreviewOptions(is_disabled=disable_web_page_preview)

        # Keep HTML parse_mode because the plugin uses <b>/<code> markup.
        return await self._client.edit_inline_text(
            self.inline_message_id,
            text,
            parse_mode=enums.ParseMode.HTML,
            link_preview_options=link_preview_options,
        )


async def _reply_ctx(client, ctx: Message, text: str, **kwargs):
    """Reply helper that supports normal chats + Guest Mode."""
    if getattr(ctx, "guest_query_id", None):
        sent = await client.answer_guest_query(
            ctx.guest_query_id,
            result=InlineQueryResultArticle(
                "Reply",
                input_message_content=InputTextMessageContent(
                    text,
                    parse_mode=enums.ParseMode.HTML,
                ),
            ),
        )
        return _GuestInlineMessage(client, sent.inline_message_id)

    return await ctx.reply_msg(text, **kwargs)


async def _progress_ctx(client, ctx: Message, strings):
    """Create 'processing' message that can be edited later."""
    if getattr(ctx, "guest_query_id", None):
        sent = await client.answer_guest_query(
            ctx.guest_query_id,
            result=InlineQueryResultArticle(
                "Processing...",
                input_message_content=InputTextMessageContent(
                    strings("find_answers_str"),
                    parse_mode=enums.ParseMode.HTML,
                ),
            ),
        )
        return _GuestInlineMessage(client, sent.inline_message_id)

    return await ctx.reply_msg(strings("find_answers_str"), quote=True)

from misskaty import BOT_USERNAME, app
from misskaty.core import pyro_cooldown
from misskaty.helper import check_time_gap, use_chat_lang
from misskaty.vars import (
    COMMAND_HANDLER,
    NINE_ROUTER_API_KEY,
    NINE_ROUTER_BASE_URL,
    NINE_ROUTER_MODEL_AI,
    NINE_ROUTER_MODEL_ASK,
    OWNER_ID,
    SUDO,
)


def _extract_guest_prompt(ctx: Message) -> str:
    """Extract user prompt when the bot is summoned in Guest Mode.

    Handles both:
    - Single mention: "@BotUsername <prompt>"
    - Multi-bot messages (each bot per line), e.g.
        "@BotA foo\n@BotB bar"
      In this case, we only take the line(s) belonging to this bot.

    Note: In Guest Mode, Kurigram will deliver the same source message text to each
    mentioned guest bot (up to 3). Each bot should extract its own segment.
    """
    raw_text = (ctx.text or ctx.caption or "")
    text = raw_text.strip()
    if not text:
        return ""

    if not BOT_USERNAME:
        return text

    mention = f"@{BOT_USERNAME}".lower()

    # Prefer line-based addressing: each bot starts a line with @BotUsername
    lines = raw_text.splitlines()
    captured: list[str] = []
    capturing = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            # Keep blank lines only if we are already capturing (acts as spacing)
            if capturing and captured:
                captured.append("")
            continue

        low = stripped.lower()

        # Start capturing when we hit our mention at beginning of a line
        if low.startswith(mention):
            capturing = True
            after = stripped[len(mention):].lstrip(" \t:-")
            if after:
                captured.append(after)
            continue

        if capturing:
            # Stop when another bot mention line begins
            if low.startswith("@"):
                break
            # Otherwise treat as continuation line
            captured.append(stripped)

    if capturing:
        # normalize: trim trailing empty lines
        while captured and captured[-1] == "":
            captured.pop()
        return "\n".join(captured).strip()

    # Fallback: inline mention somewhere in the message
    idx = text.lower().find(mention)
    if idx != -1:
        return text[idx + len(mention):].lstrip(" \t:-")

    return text

__MODULE__ = "ChatBot"
__HELP__ = """
/ai - Generate text response from AI using Mimo via 9Router.
/ask - Generate text response from AI using DeepSeek via 9Router.
"""

gptai_conversations = TTLCache(maxsize=4000, ttl=24*60*60)
gemini_conversations = TTLCache(maxsize=4000, ttl=24*60*60)

RICH_THINKING_HTML = "<tg-thinking>🤔 <b>Mikir...</b></tg-thinking>"


def _is_private_chat(ctx: Message) -> bool:
    """True when we can use rich messages/drafts: private DM, not guest inline."""
    if getattr(ctx, "guest_query_id", None):
        return False
    return getattr(ctx.chat, "type", None) == enums.ChatType.PRIVATE


async def _deliver_error(client, ctx, bmsg, err: str, rich_mode: bool):
    """Kirim pesan error: rich message di private, edit_msg di tempat lain."""
    if rich_mode:
        await client.send_rich_message(ctx.chat.id, InputRichMessage(html=err))
    else:
        await bmsg.edit_msg(err)


async def _deliver_result(client, ctx, bmsg, text: str, strings, rich_mode: bool):
    """Kirim hasil: rich message di private, edit_msg di tempat lain."""
    if len(text) > 4000:
        answerlink = await privatebinapi.send_async(
            "https://bin.yasirweb.eu.org",
            text=text,
            expiration="1week",
            formatting="markdown",
        )
        text = strings("answers_too_long").format(
            answerlink=answerlink.get("full_url")
        )
    if rich_mode:
        await client.send_rich_message(ctx.chat.id, InputRichMessage(html=text))
    else:
        await bmsg.edit_msg(text, disable_web_page_preview=True)


async def _edit_result(client, ctx, bmsg, text: str, strings):
    """Send final answer: rich message in private, edit_msg elsewhere."""
    rich_mode = ctx is not None and _is_private_chat(ctx)
    await _deliver_result(client, ctx, bmsg, text, strings, rich_mode)


async def get_openai_stream_response(
    client, is_stream, key, base_url, model, messages, bmsg, strings, ctx=None
):
    ai = AsyncOpenAI(api_key=key, base_url=base_url)
    answer = ""
    num = 0
    rich_mode = ctx is not None and _is_private_chat(ctx) and is_stream
    draft_id = None
    if rich_mode:
        draft_id = client.rnd_id()
        await client.send_rich_message_draft(
            ctx.chat.id,
            draft_id,
            InputRichMessage(html=RICH_THINKING_HTML),
        )
    try:
        response = await ai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            stream=is_stream,
        )
        if not is_stream:
            answer += response.choices[0].message.content or ""
            if rich_mode:
                await _edit_result(client, ctx, bmsg, f"{html.escape(answer)}\n\n<b>Powered by:</b> <code>{model}</code>", strings)
            else:
                await _edit_result(client, ctx, bmsg, f"{html.escape(answer)}\n\n<b>Powered by:</b> <code>{model}</code>", strings)
        else:
            async for chunk in response:
                if not chunk.choices or not chunk.choices[0].delta.content:
                    continue
                num += 1
                answer += chunk.choices[0].delta.content
                if rich_mode:
                    # Streaming preview via rich draft (same draft_id = animated)
                    try:
                        await client.send_rich_message_draft(
                            ctx.chat.id,
                            draft_id,
                            InputRichMessage(html=html.escape(answer)),
                        )
                    except Exception:
                        pass
                else:
                    if num == 30 and len(answer) < 4000:
                        await bmsg.edit_msg(html.escape(answer))
                        await asyncio.sleep(1.5)
                        num = 0
            final = f"{html.escape(answer)}\n\n<b>Powered by:</b> <code>{model}</code>"
            await _edit_result(client, ctx, bmsg, final, strings)
    except APIConnectionError as e:
        await _deliver_error(client, ctx, bmsg, f"The server could not be reached because {e.__cause__}", rich_mode)
        return None
    except RateLimitError as e:
        err = "You're got rate limit, please try again later."
        if "billing details" in str(e):
            err = "This openai key from this bot has expired, please give openai key donation for bot owner."
        await _deliver_error(client, ctx, bmsg, err, rich_mode)
        return None
    except APIStatusError as e:
        await _deliver_error(
            client, ctx, bmsg,
            f"Another {e.status_code} status code was received with response {e.response}",
            rich_mode,
        )
        return None
    except Exception as e:
        await _deliver_error(client, ctx, bmsg, f"ERROR: {e}", rich_mode)
        return None
    return answer


@app.on_message(filters.command("ai", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@app.on_business_message(
    filters.command("ai", COMMAND_HANDLER) & pyro_cooldown.wait(10)
)
# Guest Mode: triggered by mention/reply, not by /command in that chat
@app.on_guest_message(filters.text)
@use_chat_lang()
async def gemini_chatbot(client, ctx: Message, strings):
    # Normal mode uses: /ai <prompt>
    # Guest mode uses:  @BotUsername <prompt>
    if getattr(ctx, "guest_query_id", None):
        prompt = _extract_guest_prompt(ctx)
        if not prompt:
            return await _reply_ctx(
                client,
                ctx,
                (
                    f"Ketik: @{BOT_USERNAME} <pertanyaan>\n"
                    f"Atau: @{BOT_USERNAME} ai <pertanyaan> / @{BOT_USERNAME} ask <pertanyaan>"
                )
                if BOT_USERNAME
                else "Ketik: @bot <pertanyaan>",
                del_in=8,
            )

        low = prompt.strip().lower()
        # If user explicitly targets OpenAI handler in Guest Mode, don't double-handle.
        if low.startswith("/ask") or low.startswith("ask "):
            return

        # Optional explicit selector: "ai ..." or "/ai ..."
        if low.startswith("/ai"):
            prompt = prompt.strip()[len("/ai"):].lstrip(" \t:-")
        elif low.startswith("ai "):
            prompt = prompt.strip()[len("ai "):].lstrip(" \t:-")

        user_content = prompt
        model = NINE_ROUTER_MODEL_ASK  # guest mode -> deepseek
    else:
        if len(ctx.command) == 1:
            return await _reply_ctx(
                client,
                ctx,
                strings("no_question").format(cmd=ctx.command[0]),
                quote=True,
                del_in=5,
            )
        user_content = ctx.input
        model = NINE_ROUTER_MODEL_AI  # /ai -> mimo

    if not NINE_ROUTER_API_KEY:
        return await _reply_ctx(client, ctx, "NINE_ROUTER_API_KEY env is missing!!!")

    uid = (
        ctx.guest_bot_caller_user.id
        if getattr(ctx, "guest_query_id", None) and getattr(ctx, "guest_bot_caller_user", None)
        else (ctx.from_user.id if ctx.from_user else ctx.sender_chat.id)
    )

    msg = None if _is_private_chat(ctx) else await _progress_ctx(client, ctx, strings)
    if uid not in gemini_conversations:
        gemini_conversations[uid] = [
            {
                "role": "system",
                "content": "Kamu adalah AI dengan karakter mirip kucing bernama MissKaty AI yang diciptakan oleh Yasir untuk membantu manusia mencari informasi dan gunakan bahasa sesuai yang saya katakan.",
            },
            {"role": "user", "content": user_content},
        ]
    else:
        gemini_conversations[uid].append({"role": "user", "content": user_content})
    ai_response = await get_openai_stream_response(
        client, True, NINE_ROUTER_API_KEY, NINE_ROUTER_BASE_URL, model,
        gemini_conversations[uid], msg, strings, ctx,
    )
    if not ai_response:
        gemini_conversations[uid].pop()
        if len(gemini_conversations[uid]) == 1:
            gemini_conversations.pop(uid)
        return
    gemini_conversations[uid].append({"role": "assistant", "content": ai_response})

@app.on_message(filters.command("ask", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@app.on_business_message(
    filters.command("ask", COMMAND_HANDLER) & pyro_cooldown.wait(10)
)
# Guest Mode: triggered by mention/reply, not by /command in that chat
@app.on_guest_message(filters.text)
@use_chat_lang()
async def openai_chatbot(client, ctx: Message, strings):
    # Normal mode uses: /ask <prompt>
    # Guest mode uses:  @BotUsername <prompt>
    if getattr(ctx, "guest_query_id", None):
        prompt = _extract_guest_prompt(ctx)
        if not prompt:
            return await _reply_ctx(
                client,
                ctx,
                (
                    f"Ketik: @{BOT_USERNAME} <pertanyaan>\n"
                    f"Atau: @{BOT_USERNAME} ai <pertanyaan> / @{BOT_USERNAME} ask <pertanyaan>"
                )
                if BOT_USERNAME
                else "Ketik: @bot <pertanyaan>",
                del_in=8,
            )

        low = prompt.strip().lower()

        # Only handle Guest Mode when explicitly selected with "ask".
        # Otherwise, default guest mentions are handled by gemini_chatbot to avoid double replies.
        if low.startswith("/ask"):
            prompt = prompt.strip()[len("/ask"):].lstrip(" \t:-")
        elif low.startswith("ask "):
            prompt = prompt.strip()[len("ask "):].lstrip(" \t:-")
        else:
            return

        user_content = prompt
    else:
        if len(ctx.command) == 1:
            return await _reply_ctx(
                client,
                ctx,
                strings("no_question").format(cmd=ctx.command[0]),
                quote=True,
                del_in=5,
            )
        user_content = ctx.input

    if not NINE_ROUTER_API_KEY:
        return await _reply_ctx(client, ctx, "NINE_ROUTER_API_KEY env is missing!!!")

    uid = (
        ctx.guest_bot_caller_user.id
        if getattr(ctx, "guest_query_id", None) and getattr(ctx, "guest_bot_caller_user", None)
        else (ctx.from_user.id if ctx.from_user else ctx.sender_chat.id)
    )

    is_in_gap, _ = await check_time_gap(uid)
    if is_in_gap and (uid != OWNER_ID or uid not in SUDO):
        return await _reply_ctx(client, ctx, strings("dont_spam"), del_in=5)

    pertanyaan = user_content
    msg = None if _is_private_chat(ctx) else await _progress_ctx(client, ctx, strings)
    if uid not in gptai_conversations:
        gptai_conversations[uid] = [
            {
                "role": "system",
                "content": "Kamu adalah AI dengan karakter mirip kucing bernama MissKaty AI yang diciptakan oleh Yasir untuk membantu manusia mencari informasi dan gunakan bahasa sesuai yang saya katakan.",
            },
            {"role": "user", "content": pertanyaan},
        ]
    else:
        gptai_conversations[uid].append({"role": "user", "content": pertanyaan})
    ai_response = await get_openai_stream_response(
        client, True, NINE_ROUTER_API_KEY, NINE_ROUTER_BASE_URL, NINE_ROUTER_MODEL_ASK,
        gptai_conversations[uid], msg, strings, ctx,
    )
    if not ai_response:
        gptai_conversations[uid].pop()
        if len(gptai_conversations[uid]) == 1:
            gptai_conversations.pop(uid)
        return
    gptai_conversations[uid].append({"role": "assistant", "content": ai_response})
