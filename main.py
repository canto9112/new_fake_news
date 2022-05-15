import aiohttp
import asyncio
import requests
from adapters.inosmi_ru import sanitize
import pymorphy2

from text_tools import split_by_words, calculate_jaundice_rate
from anyio import sleep, create_task_group, run


def _clean_word(word):
    word = word.replace('<div>', '').replace('<.div>', '')
    # FIXME какие еще знаки пунктуации часто встречаются ?
    return word

async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()

async def process_article(session, morph, charged_words, url):
    html = await fetch(session, url)
    clean_text = sanitize(html)
    clean_text = clean_text.replace('<div>', '').replace('</div>', '')
    words = split_by_words(morph, clean_text)
    round = calculate_jaundice_rate(words, charged_words)
    print(round)
    await sleep(0.5)


async def main():
    morph = pymorphy2.MorphAnalyzer()
    with open("archive/negative_words.txt") as f:
        negative_words = f.read().splitlines()
    with open("archive/positive_words.txt") as f:
        positive_words = f.read().splitlines()
    charged_words = negative_words + positive_words

    TEST_ARTICLES = [
        "https://inosmi.ru/economic/20190629/245384784.html",
        "https://inosmi.ru/20220113/251289901.html",
        "https://inosmi.ru/20210729/250219930.html"
    ]
    async with aiohttp.ClientSession() as session:
        async with create_task_group() as tg:
            for url in TEST_ARTICLES:
                tg.start_soon(process_article, session, morph, charged_words, url)

        print('All tasks finished!')

asyncio.run(main())
