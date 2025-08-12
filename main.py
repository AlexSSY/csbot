import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
import requests
from io import BytesIO

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


CURRENT_DIR = Path(__file__).resolve().parent


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


@dataclass
class Order:
    name: str
    image_url: str
    price: str
    discount: int


def make_order_from_json(json_order_dict: Dict[str, Any]) -> Order:
    asset = json_order_dict.get('asset')
    name = asset.get('names').get('full')
    image_url = asset.get('images').get('preview')
    price = json_order_dict.get('pricing').get('computed')
    discount = json_order_dict.get('pricing').get('discount')
    return Order(name=name, image_url=image_url, price=price, discount=discount)


def get_orders_dict_from_website(url: str) -> Dict[str, Any]:
    profile_path = CURRENT_DIR / '.profile'

    if not os.path.exists(profile_path):
        os.mkdir(profile_path)

    options = Options()
    options.headless = True  # ghost-режим
    options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0")
    options.set_preference("network.cookie.cookieBehavior", 0)  # разрешить куки
    options.set_preference("javascript.enabled", True)  # JS включен
    options.set_preference("devtools.jsonview.enabled", False)  # выключаем обёртку JSON в HTML
    options.profile = webdriver.FirefoxProfile(profile_path)

    driver = webdriver.Firefox(options=options)
    driver.get(url)
    raw_json = driver.find_element("tag name", "pre").text
    json_response = json.loads(raw_json)
    driver.quit()

    return json_response.get('items')


def get_orders(limit: int = 3) -> List[Order]:
    orders_list = get_orders_dict_from_website(
        f'https://cs.money/2.0/market/sell-orders?limit={limit}&offset=0&order=desc&sort=discount'
    )

    return [
        make_order_from_json(item) for
        item in orders_list
    ]


def adjust_preview_image(image_url: str) -> BufferedInputFile:
    # Скачиваем PNG
    resp = requests.get(image_url)
    img = Image.open(BytesIO(resp.content)).convert("RGBA")

    # Накладываем фон
    background = Image.new("RGBA", img.size, (40, 40, 40, 255))  # темно-серый фон
    background.paste(img, mask=img)

    # Конвертируем в JPEG
    output = BytesIO()
    background.convert("RGB").save(output, format="JPEG")
    output.seek(0)
    return BufferedInputFile(output.read(), filename="image.jpg")


# Command handler
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    for order in get_orders():
        await message.answer_photo(
            photo=adjust_preview_image(order.image_url),
            caption=f'<b>{order.name}</b>\n\n<b>Price:</b> {order.price}$\n<b>Discount:</b> {int(order.discount * 100)}%',
            parse_mode='html'
        )


# Run the bot
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
