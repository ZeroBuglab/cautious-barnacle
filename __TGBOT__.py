from aiogram.types import BufferedInputFile
import io
import asyncio
import datetime
import requests
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import mplfinance as mpf
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "YOUR TOKEN"
SYMBOL_DEFAULT = "BTCUSDT"
INTERVAL_DEFAULT = "1h"
CANDLES_DEFAULT = 24
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)
subscribers: set[int] = set()


def fetch_klines_binance(symbol: str, interval: str, limit: int) -> pd.DataFrame:
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if not data:
        raise RuntimeError("Пустой ответ от Binance")

    df = pd.DataFrame(
        data,
        columns=[
            "time", "open", "high", "low", "close",
            "volume", "close_time", "qav", "num_trades",
            "taker_base_vol", "taker_quote_vol", "ignore"
        ],
    )

    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df.set_index("time", inplace=True)


    cols = ["open", "high", "low", "close", "volume"]
    df[cols] = df[cols].astype(float)


    df = df.rename(
        columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )

    return df[["Open", "High", "Low", "Close", "Volume"]]

def render_chart_to_bytes(df: pd.DataFrame, symbol: str) -> bytes:

    buf = io.BytesIO()
    mpf.plot(
        df,
        type="candle",
        mav=(7, 14),
        volume=True,
        style="charles",
        savefig=dict(fname=buf, dpi=120, bbox_inches="tight"),
    )
    buf.seek(0)
    return buf.read()


async def make_chart_async(symbol: str = SYMBOL_DEFAULT,
                           interval: str = INTERVAL_DEFAULT,
                           limit: int = CANDLES_DEFAULT) -> bytes:

    loop = asyncio.get_running_loop()
    df = await loop.run_in_executor(None, fetch_klines_binance, symbol, interval, limit)
    png_bytes = await loop.run_in_executor(None, render_chart_to_bytes, df, symbol)
    return png_bytes


@router.message(Command("start"))
async def cmd_start(message: Message):
    subscribers.add(message.chat.id)
    await message.answer(
        "Привет! Я присылаю графики крипты \n"
        "Команды:\n"
        "• /btc — график BTC/USDT (последние 24 свечи 1h)\n"
        "• /sub — подписаться на авто-рассылку каждый час\n"
        "• /unsub — отписаться от авто-рассылки\n"
    )

@router.message(Command("btc"))
async def cmd_btc(message: Message):
    try:
        png = await make_chart_async("BTCUSDT", "1h", 24)
        photo = BufferedInputFile(png,filename="chart.png")
        await message.answer_photo(
            photo=photo,
            caption=f"📊 BTC/USDT — последние 24 часа (на {datetime.datetime.now():%d.%m %H:%M})"
        )
    except Exception as e:
        await message.answer(f"⚠️ Не удалось построить график: {e}")

@router.message(Command("sub"))
async def cmd_sub(message: Message):
    subscribers.add(message.chat.id)
    await message.answer("✅ Подписка оформлена. Буду присылать график каждый час.")

@router.message(Command("unsub"))
async def cmd_unsub(message: Message):
    subscribers.discard(message.chat.id)
    await message.answer("❌ Подписка отключена. Больше не буду присылать графики по расписанию.")


async def broadcast_chart():
    if not subscribers:
        return
    try:
        png = await make_chart_async("BTCUSDT", "1h", 24)
    except Exception as e:
        print(f"[broadcast] ошибка построения графика: {e}")
        return

    for chat_id in list(subscribers):
        try:
            photo = BufferedInputFile(png,filename="chart.png")
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"⏰ Ежечасный график BTC/USDT (на {datetime.datetime.now():%d.%m %H:%M})"
            )
        except Exception as e:
            print(f"[broadcast] не удалось отправить {chat_id}: {e}")


async def main():
    print("🤖 Бот запускается...")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(broadcast_chart, "interval", minutes=60)
    scheduler.start()

    print("✅ Бот запущен. Ожидаю сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

