import asyncio
import requests
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


class Order(dataclass):
    name: str
    image_url: str
    price: str
    discount: int


def get_orders(limit: int = 3) -> list[Order]:
    REQUEST_URL = 'https://cs.money/2.0/market/sell-orders?limit=60&offset=0&order=desc&sort=discount'

    REQUEST_HEADERS = {
        'Host': 'cs.money',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://cs.money/market/buy/',
        'traceparent': '00-666e691b9ed39b28dafe44bedeb3a41f-0ae21f179dd7e7ab-01',
        'Content-Type': 'application/json',
        'X-Client-App': 'web',
        'sentry-trace': '226722efa60665a296e72825a967c533-8040cfda3b668531-0',
        'baggage': 'sentry-environment=production,sentry-release=2025-08-11-1140-production,sentry-public_key=da19e2c6e5d741efbda9d313341ab6d6,sentry-trace_id=226722efa60665a296e72825a967c533,sentry-sampled=false,sentry-sample_rand=0.36917547928665484,sentry-sample_rate=0.2',
        'Connection': 'keep-alive',
        'Cookie': 'registered_user=true; cc_service2={%22services%22:[%22necessary%22%2C%22gtm%22%2C%22ym%22%2C%22amplitude%22%2C%22gleam%22%2C%22esputnik%22%2C%22hotjar%22%2C%22userSesDatToAnalytic%22%2C%22userSesDatToMarketing%22%2C%22cardVisualSize%22]%2C%22acceptanceDate%22:1754929562474%2C%22revision%22:0%2C%22additionalData%22:{%22country%22:%22UA%22}}; group_id=47392a0d-09cd-4f32-83d0-d59750568886; session_timer_104055=1; session_timer_-1653249155=1; sc=CE8700B5-C973-1929-D248-C4885030B9B6; GleamId=pWoSJ1EYBj5IRhQfB; GleamA=%7B%22pWoSJ%22%3A%22%22%7D; _gcl_au=1.1.1667355753.1754929564; amplitude_id_c14fa5162b6e034d1c3b12854f3a26f5cs.money=eyJkZXZpY2VJZCI6ImIwZGIzOGUyLTI1NGEtNGM0MC05OWE0LTUyNTFlNzhmMDlkNlIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTc1NDkyOTU2NDA5MSwibGFzdEV2ZW50VGltZSI6MTc1NDkyOTU5NzE2MywiZXZlbnRJZCI6NSwiaWRlbnRpZnlJZCI6NSwic2VxdWVuY2VOdW1iZXIiOjEwfQ==; cf_clearance=LW2iVDlXqvgv8XGz2W0IBfZg5bcQWJVnpS7te7LhwB0-1754929564-1.2.1.1-HJV8RGT6BBUZ.C1splOMErOjSPiJKK3vsnTFd_qe4QXuH7jCVMNvAcT_fEuQQ6WqLD6EScumYFJp9dCRiHiaCuGP2R1R.IQ.ee5jc7hzyiDut7s3Jk8nflwQE0gPLiQHIRJV.te_95y9w.df180.NQv3QSGqJtfF0UOoXC0ImpMQy0W4B84ewqdyd2IUp8fye7eUynzFaLO3oCCRAKIZBo3ZP1TIFjCNOfM8S8stFbk; _scid=s_xoDqCnBdhGR7dBpNEMduUBJI5G2VJJ; _ga_HY7CCPCD7H=GS2.1.s1754929563$o1$g1$t1754929601$j22$l0$h0; _ga=GA1.1.1245522423.1754929564; _fbp=fb.1.1754929564831.714345553348843478; _ym_uid=175492956583408211; _ym_d=1754929565; _hjSessionUser_2848248=eyJpZCI6IjkzZmIwMWY4LWFlODktNTk1Ny04MTk1LWRhYTMzMmM0MDJmOSIsImNyZWF0ZWQiOjE3NTQ5Mjk1NjUyMjEsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_2848248=eyJpZCI6ImQ2Zjg3OTE3LTg0MjQtNGNjYi1hNmIzLTMwNTM1YzVmZmU0YiIsImMiOjE3NTQ5Mjk1NjUyMjIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MX0=; _hjHasCachedUserAttributes=true; _ym_isad=2; _sctr=1%7C1754859600000; _ym_visorc=w; was_called_in_current_session_104055=1; user_currency=USD; user_locale=en; isAnalyticEventsLimit=true; seconds_on_page_104055=31; seconds_on_page_-1653249155=31; was_called_in_current_session_-1653249155=1; u_vp=1233x926; csp-nonce=OTg1NzE1ZTAtNmE0MS00MWJmLThkZmQtZDM0ZDc2OGYyYzcy; u_dpi=1; settings_visual_card_size=large; AMP_c14fa5162b=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI3NzdhNzNhZi0zOGNiLTRhZjMtOTFmNi0xZmU0ZmY3ZjRiYTUlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzU0OTI5NjAyNDY3JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc1NDkyOTYwMjYzMSUyQyUyMmxhc3RFdmVudElkJTIyJTNBNSUyQyUyMnBhZ2VDb3VudGVyJTIyJTNBMSU3RA==; _scid_r=vXxoDqCnBdhGR7dBpNEMduUBJI5G2VJJb8kZtg; _uetsid=e0b2c2b076cf11f0a4d32552912787df|og5zm0|2|fyd|0|2049; _uetvid=e0b2dc1076cf11f0887405e1fde496dd|10ykub0|1754929602727|3|1|bat.bing.com/p/insights/c/j',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'If-None-Match': 'W/"198a2-1dzU79uOAcyaQ3oJRyDAwp/d1NA"',
        'Priority': 'u=4',
        'TE': 'trailers'
    }

    # make request
    response = requests.get(url=REQUEST_URL, headers=REQUEST_HEADERS)

    if response.ok:

        try:
            json_response = response.json()
        except:
            print("Failed to parse response as JSON")

        orders_list = json_response.get('items')
        size = max(limit, len(orders_list))
        orders_list = orders_list[:size]

        return [
            Order(name=item.get('name')) for
            item in orders_list
        ]
    
    return []


# Command handler
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Hello! I'm a bot created with aiogram.")


# Run the bot
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
