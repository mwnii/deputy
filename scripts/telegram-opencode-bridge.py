#!/usr/bin/env python3
"""
Telegram-to-OpenCode Bridge
Sends voice notes and text messages from Telegram to opencode and returns responses.
"""

import asyncio
import logging
import os
import sys
import tempfile
from pathlib import Path

import httpx
from groq import Groq
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("tg-bridge")

ENV_FILE = Path(__file__).parent / ".env.telegram"

TELEGRAM_BOT_TOKEN = ""
TELEGRAM_USER_ID = 0
GROQ_API_KEY = ""
OPENCODE_HOST = "http://127.0.0.1"
OPENCODE_PORT = 4096


def load_env():
    global TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID, GROQ_API_KEY
    global OPENCODE_HOST, OPENCODE_PORT

    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_USER_ID = int(os.environ.get("TELEGRAM_USER_ID", "0"))
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    OPENCODE_HOST = os.environ.get("OPENCODE_HOST", "http://127.0.0.1")
    OPENCODE_PORT = int(os.environ.get("OPENCODE_PORT", "4096"))

    missing = []
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_USER_ID:
        missing.append("TELEGRAM_USER_ID")
    if not GROQ_API_KEY or GROQ_API_KEY == "PASTE_YOUR_GROQ_API_KEY_HERE":
        missing.append("GROQ_API_KEY")
    if missing:
        logger.error("Missing required env vars: %s", ", ".join(missing))
        logger.error("Edit .env.telegram and fill in your credentials.")
        sys.exit(1)


class OpenCodeClient:
    def __init__(self, host: str, port: int):
        self.base = f"{host}:{port}"
        self.session_id: str | None = None
        self.http = httpx.AsyncClient(base_url=self.base, timeout=300.0)

    async def _create_session(self) -> str:
        resp = await self.http.post("/session", json={"title": "Telegram Bridge"})
        resp.raise_for_status()
        self.session_id = resp.json()["id"]
        logger.info("Created opencode session: %s", self.session_id)
        return self.session_id

    async def validate_session(self) -> bool:
        if not self.session_id:
            return False
        try:
            resp = await self.http.get(f"/session/{self.session_id}")
            return resp.status_code == 200
        except Exception:
            return False

    async def ensure_session(self) -> str:
        if self.session_id and await self.validate_session():
            return self.session_id
        logger.info("Session invalid or missing, creating new session")
        return await self._create_session()

    async def _send_raw(self, text: str) -> str:
        session_id = await self.ensure_session()
        resp = await self.http.post(
            f"/session/{session_id}/message",
            json={
                "agent": "ea",
                "parts": [{"type": "text", "text": text}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        parts = data.get("parts", [])
        text_parts = [p["text"] for p in parts if p.get("type") == "text"]
        return "\n".join(text_parts) if text_parts else "(no text response)"

    async def send_prompt(self, text: str, status_callback: object | None = None) -> str:
        # Try current session first
        try:
            return await self._send_raw(text)
        except Exception as e:
            logger.warning(
                "First attempt failed (%s: %s), retrying same session",
                type(e).__name__,
                e,
            )

        # Retry same session once (server may have been busy)
        if status_callback:
            await status_callback("Server busy, retrying...")
        try:
            return await self._send_raw(text)
        except Exception as e:
            logger.warning(
                "Second attempt failed (%s: %s), creating new session",
                type(e).__name__,
                e,
            )

        # Only then create a new session
        self.session_id = None
        try:
            return await self._send_raw(text)
        except Exception as e:
            logger.error("Third attempt failed (%s: %s)", type(e).__name__, e)
            raise

    async def close(self):
        await self.http.aclose()


class Transcriber:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def transcribe_file(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            result = self.client.audio.transcriptions.create(
                file=(Path(file_path).name, f.read()),
                model="whisper-large-v3",
                language="en",
            )
        return result.text


oc_client: OpenCodeClient | None = None
transcriber: Transcriber | None = None


def is_authorized(update: Update) -> bool:
    user_id = update.effective_user.id if update.effective_user else 0
    return user_id == TELEGRAM_USER_ID


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("Unauthorized.")
        return
    await update.message.reply_text(
        "Telegram-OpenCode Bridge active.\n\n"
        "Send text messages or voice notes. I'll forward them to opencode "
        "and return the response.\n\n"
        "Commands:\n"
        "/start - This message\n"
        "/new - Start a new opencode session\n"
        "/status - Check connection status\n"
        "/cancel - Cancel a stuck request"
    )


async def cmd_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    global oc_client
    if oc_client:
        await oc_client.close()
    oc_client = OpenCodeClient(OPENCODE_HOST, OPENCODE_PORT)
    await oc_client.ensure_session()
    await update.message.reply_text("New opencode session created.")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{OPENCODE_HOST}:{OPENCODE_PORT}/global/health", timeout=5.0)
            if r.status_code == 200:
                info = r.json()
                await update.message.reply_text(
                    f"opencode: running (v{info.get('version', '?')})\n"
                    f"Session: {oc_client.session_id or 'none'}"
                )
            else:
                await update.message.reply_text(f"opencode responded with {r.status_code}")
    except Exception as e:
        await update.message.reply_text(f"Cannot reach opencode: {e}")


# Global set to track cancel requests
_cancel_events: dict[int, asyncio.Event] = {}


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    user_id = update.effective_user.id
    event = _cancel_events.get(user_id)
    if event:
        event.set()
        await update.message.reply_text(
            "Cancel signal sent. Waiting for current request to stop..."
        )
    else:
        await update.message.reply_text("No active request to cancel.")


async def _periodic_status_edit(status_msg, elapsed_ref, cancel_event):
    """Edit the status message every 60s to show elapsed time."""
    while True:
        try:
            await asyncio.wait_for(cancel_event.wait(), timeout=60)
            return  # cancelled
        except asyncio.TimeoutError:
            elapsed_ref[0] += 60
            try:
                await status_msg.edit_text(f"Thinking... ({elapsed_ref[0]}s elapsed)")
            except Exception:
                pass


def _make_status_cb(status_msg, parse_mode=None):
    """Create an async status callback for send_prompt."""

    async def status_cb(msg):
        try:
            await status_msg.edit_text(msg, parse_mode=parse_mode)
        except Exception:
            pass

    return status_cb


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("Unauthorized.")
        return

    text = update.message.text
    if not text:
        return

    logger.info("Text from %s: %s", update.effective_user.first_name, text[:80])

    status_msg = await update.message.reply_text("Thinking...")
    elapsed_ref = [0]
    cancel_event = asyncio.Event()
    _cancel_events[update.effective_user.id] = cancel_event
    timer = asyncio.create_task(_periodic_status_edit(status_msg, elapsed_ref, cancel_event))

    try:
        response = await oc_client.send_prompt(text, status_callback=_make_status_cb(status_msg))
        for chunk in split_message(response):
            await update.message.reply_text(chunk)
        await status_msg.delete()
    except Exception as e:
        logger.error("opencode error (%s: %s)", type(e).__name__, e)
        await status_msg.edit_text("Error: Could not reach OpenCode server. Please try again.")
    finally:
        timer.cancel()
        cancel_event.set()
        _cancel_events.pop(update.effective_user.id, None)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    voice = update.message.voice
    if not voice:
        return

    status_msg = await update.message.reply_text("Transcribing voice note...")

    try:
        file = await context.bot.get_file(voice.file_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            tmp_path = tmp.name
            await file.download_to_drive(tmp_path)

        logger.info("Voice downloaded to %s (%d seconds)", tmp_path, voice.duration or 0)

        text = await asyncio.get_event_loop().run_in_executor(
            None, transcriber.transcribe_file, tmp_path
        )

        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        if not text.strip():
            await status_msg.edit_text("Could not transcribe voice note.")
            return

        logger.info("Transcribed: %s", text[:80])

        await status_msg.edit_text(
            f"Transcribed: _{text}_\n\nSending to opencode...",
            parse_mode="Markdown",
        )

        elapsed_ref = [0]
        cancel_event = asyncio.Event()
        _cancel_events[update.effective_user.id] = cancel_event
        timer = asyncio.create_task(_periodic_status_edit(status_msg, elapsed_ref, cancel_event))

        try:
            response = await oc_client.send_prompt(
                text,
                status_callback=_make_status_cb(status_msg, parse_mode="Markdown"),
            )
            for chunk in split_message(response):
                await update.message.reply_text(chunk)
            await status_msg.delete()
        finally:
            timer.cancel()
            cancel_event.set()
            _cancel_events.pop(update.effective_user.id, None)

    except Exception as e:
        logger.error("Voice processing error (%s: %s)", type(e).__name__, e)
        await status_msg.edit_text("Voice processing failed. Please try again.")


async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    video_note = update.message.video_note
    if not video_note:
        return

    status_msg = await update.message.reply_text("Transcribing video note...")

    try:
        file = await context.bot.get_file(video_note.file_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp_path = tmp.name
            await file.download_to_drive(tmp_path)

        text = await asyncio.get_event_loop().run_in_executor(
            None, transcriber.transcribe_file, tmp_path
        )

        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        if not text.strip():
            await status_msg.edit_text("Could not transcribe video note.")
            return

        await status_msg.edit_text(
            f"Transcribed: _{text}_\n\nSending to opencode...",
            parse_mode="Markdown",
        )

        elapsed_ref = [0]
        cancel_event = asyncio.Event()
        _cancel_events[update.effective_user.id] = cancel_event
        timer = asyncio.create_task(_periodic_status_edit(status_msg, elapsed_ref, cancel_event))

        try:
            response = await oc_client.send_prompt(
                text,
                status_callback=_make_status_cb(status_msg, parse_mode="Markdown"),
            )
            for chunk in split_message(response):
                await update.message.reply_text(chunk)
            await status_msg.delete()
        finally:
            timer.cancel()
            cancel_event.set()
            _cancel_events.pop(update.effective_user.id, None)

    except Exception as e:
        logger.error("Video note error (%s: %s)", type(e).__name__, e)
        await status_msg.edit_text("Video note processing failed. Please try again.")


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    audio = update.message.audio
    if not audio:
        return

    status_msg = await update.message.reply_text("Transcribing audio...")

    try:
        file = await context.bot.get_file(audio.file_id)
        ext = Path(audio.file_name or "audio.ogg").suffix or ".ogg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp_path = tmp.name
            await file.download_to_drive(tmp_path)

        text = await asyncio.get_event_loop().run_in_executor(
            None, transcriber.transcribe_file, tmp_path
        )

        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        if not text.strip():
            await status_msg.edit_text("Could not transcribe audio.")
            return

        await status_msg.edit_text(
            f"Transcribed: _{text}_\n\nSending to opencode...",
            parse_mode="Markdown",
        )

        elapsed_ref = [0]
        cancel_event = asyncio.Event()
        _cancel_events[update.effective_user.id] = cancel_event
        timer = asyncio.create_task(_periodic_status_edit(status_msg, elapsed_ref, cancel_event))

        try:
            response = await oc_client.send_prompt(
                text,
                status_callback=_make_status_cb(status_msg, parse_mode="Markdown"),
            )
            for chunk in split_message(response):
                await update.message.reply_text(chunk)
            await status_msg.delete()
        finally:
            timer.cancel()
            cancel_event.set()
            _cancel_events.pop(update.effective_user.id, None)

    except Exception as e:
        logger.error("Audio error (%s: %s)", type(e).__name__, e)
        await status_msg.edit_text("Audio processing failed. Please try again.")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    doc = update.message.document
    if not doc:
        return

    audio_exts = {".ogg", ".oga", ".mp3", ".wav", ".m4a", ".flac", ".opus", ".wma"}
    ext = Path(doc.file_name or "").suffix.lower()

    if ext not in audio_exts:
        return

    status_msg = await update.message.reply_text("Transcribing audio file...")

    try:
        file = await context.bot.get_file(doc.file_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp_path = tmp.name
            await file.download_to_drive(tmp_path)

        text = await asyncio.get_event_loop().run_in_executor(
            None, transcriber.transcribe_file, tmp_path
        )

        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        if not text.strip():
            await status_msg.edit_text("Could not transcribe audio file.")
            return

        await status_msg.edit_text(
            f"Transcribed: _{text}_\n\nSending to opencode...",
            parse_mode="Markdown",
        )

        elapsed_ref = [0]
        cancel_event = asyncio.Event()
        _cancel_events[update.effective_user.id] = cancel_event
        timer = asyncio.create_task(_periodic_status_edit(status_msg, elapsed_ref, cancel_event))

        try:
            response = await oc_client.send_prompt(
                text,
                status_callback=_make_status_cb(status_msg, parse_mode="Markdown"),
            )
            for chunk in split_message(response):
                await update.message.reply_text(chunk)
            await status_msg.delete()
        finally:
            timer.cancel()
            cancel_event.set()
            _cancel_events.pop(update.effective_user.id, None)

    except Exception as e:
        logger.error("Document audio error (%s: %s)", type(e).__name__, e)
        await status_msg.edit_text("Audio file processing failed. Please try again.")


def split_message(text: str, max_len: int = 4000) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        idx = text.rfind("\n", 0, max_len)
        if idx == -1:
            idx = text.rfind(" ", 0, max_len)
        if idx == -1:
            idx = max_len
        else:
            idx += 1
        chunks.append(text[:idx])
        text = text[idx:]
    return chunks


async def post_init(app):
    global oc_client, transcriber
    oc_client = OpenCodeClient(OPENCODE_HOST, OPENCODE_PORT)
    transcriber = Transcriber(GROQ_API_KEY)
    await oc_client.ensure_session()
    logger.info("Bridge initialized. Session: %s", oc_client.session_id)


async def post_shutdown(app):
    global oc_client
    if oc_client:
        await oc_client.close()
    logger.info("Bridge shut down.")


def main():
    load_env()

    logger.info("Starting Telegram-OpenCode Bridge")
    logger.info("opencode server: %s:%s", OPENCODE_HOST, OPENCODE_PORT)

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    app.add_handler(MessageHandler(filters.Document.AUDIO, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot polling started. Send a message to your bot on Telegram.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
