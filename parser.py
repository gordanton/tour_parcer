import html
import json
import logging
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'ru-RU,ru;q=0.9',
}


def fetch_page(url, timeout=20):
    """Загружает HTML-страницу и возвращает текст ответа."""
    logger.info("Парсинг URL: %s", url)
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or 'utf-8'
    return response.text


def normalize_link(link, domain, page_url):
    """Преобразует относительную ссылку в абсолютную."""
    if not link:
        return ''
    if link.startswith('http'):
        return link
    base = domain or page_url
    return urljoin(base, link)


def parse_website(url, item_selector, title_selector, link_selector='a', domain=None):
    """Универсальный парсер по CSS-селекторам."""
    promotions = []
    try:
        page_html = fetch_page(url)
        soup = BeautifulSoup(page_html, 'html.parser')
        items = soup.select(item_selector)
        logger.info("Найдено блоков: %s", len(items))

        for item in items:
            try:
                title_element = item.select_one(title_selector)
                if not title_element:
                    continue
                title = title_element.get_text(strip=True)
                if not title:
                    continue

                link_element = item.select_one(link_selector)
                link = link_element.get('href') if link_element else ''
                link = normalize_link(link, domain, url)

                promotions.append({
                    'title': title,
                    'link': link,
                    'source': (domain or url).split('//')[1].split('/')[0],
                })
            except Exception as exc:
                logger.warning("Ошибка парсинга элемента: %s", exc)
    except Exception as exc:
        logger.error("Ошибка парсинга %s: %s", url, exc)
    return promotions


def parse_promotion_settings(url, domain, source):
    """Парсит window._promotion_settings (Coral Travel, Sunmar)."""
    promotions = []
    seen = set()
    try:
        page_html = fetch_page(url)
        for match in re.finditer(
            r'name:\s*"([^"]+)"[\s\S]{0,400}?url:\s*"([^"]+)"',
            page_html,
        ):
            title = match.group(1).strip()
            link = normalize_link(match.group(2).strip(), domain, url)
            key = (title, link)
            if key in seen:
                continue
            seen.add(key)
            promotions.append({
                'title': title,
                'link': link,
                'source': source,
            })
        logger.info("Найдено предложений (_promotion_settings): %s", len(promotions))
    except Exception as exc:
        logger.error("Ошибка парсинга %s: %s", url, exc)
    return promotions


def parse_elementor_posts(url, domain, source):
    """Парсит карточки акций FUN&SUN (WordPress/Elementor)."""
    promotions = []
    seen = set()
    try:
        page_html = fetch_page(url)
        soup = BeautifulSoup(page_html, 'html.parser')

        for item in soup.select('article.elementor-post'):
            link_element = item.find('a', href=True)
            if not link_element:
                continue
            title = link_element.get_text(' ', strip=True)
            link = normalize_link(link_element.get('href', ''), domain, url)
            if not title or not link:
                continue
            key = (title, link)
            if key in seen:
                continue
            seen.add(key)
            promotions.append({
                'title': title,
                'link': link,
                'source': source,
            })
        logger.info("Найдено предложений (Elementor): %s", len(promotions))
    except Exception as exc:
        logger.error("Ошибка парсинга %s: %s", url, exc)
    return promotions


def parse_pegast_news(url, domain, source):
    """Парсит новости/акции PEGAS Touristik."""
    promotions = []
    seen = set()
    try:
        page_html = fetch_page(url)
        soup = BeautifulSoup(page_html, 'html.parser')

        for item in soup.select('.news-item'):
            link_element = item if item.name == 'a' else item.find('a', href=True)
            if not link_element:
                continue
            title = link_element.get_text(strip=True)
            link = normalize_link(link_element.get('href', ''), domain, url)
            if not title or not link:
                continue
            key = (title, link)
            if key in seen:
                continue
            seen.add(key)
            promotions.append({
                'title': title,
                'link': link,
                'source': source,
            })

        if not promotions:
            app_node = soup.find(id='app')
            if app_node and app_node.get('data-view-model'):
                payload = html.unescape(app_node['data-view-model'])
                data = json.loads(payload)
                for item in data.get('data', {}).get('items', []):
                    title = item.get('title', '').strip()
                    slug = item.get('slug', '').strip()
                    if not title:
                        continue
                    link = normalize_link(slug, domain, url)
                    key = (title, link)
                    if key in seen:
                        continue
                    seen.add(key)
                    promotions.append({
                        'title': title,
                        'link': link,
                        'source': source,
                    })

        logger.info("Найдено предложений (PEGAS): %s", len(promotions))
    except Exception as exc:
        logger.error("Ошибка парсинга %s: %s", url, exc)
    return promotions


def parse_biblioglobus():
    """Парсит акции с главной страницы Библио-Глобус."""
    url = "https://www.bgoperator.ru/"
    domain = "https://www.bgoperator.ru"
    source = "www.bgoperator.ru"
    promotions = []
    seen = set()

    try:
        page_html = fetch_page(url)
        soup = BeautifulSoup(page_html, 'html.parser')

        for link_element in soup.select('a[href*="main5.shtml"][href*="action=shw"]'):
            title = link_element.get_text(strip=True)
            link = normalize_link(link_element.get('href', ''), domain, url)
            if len(title) < 10:
                continue
            key = (title, link)
            if key in seen:
                continue
            seen.add(key)
            promotions.append({
                'title': title,
                'link': link,
                'source': source,
            })

        all_actions = soup.find('a', href=re.compile(r'docs\.shtml\?action=pc&section=140810024027'))
        if all_actions:
            title = all_actions.get_text(strip=True) or "Все акции Библио-Глобус"
            link = normalize_link(all_actions['href'], domain, url)
            key = (title, link)
            if key not in seen:
                seen.add(key)
                promotions.append({
                    'title': title,
                    'link': link,
                    'source': source,
                })

        logger.info("Найдено предложений (Библио-Глобус): %s", len(promotions))
    except Exception as exc:
        logger.error("Ошибка парсинга Библио-Глобус: %s", exc)
    return promotions


def parse_coral():
    return parse_promotion_settings(
        url="https://www.coral.ru/poleznaya-informatsiya/offers/hot-offers/",
        domain="https://www.coral.ru",
        source="www.coral.ru",
    )


def parse_anex():
    """
    Парсит акции Anex Tour.
    Страница /actions отдает данные через JavaScript, поэтому используем
    главную страницу и резервный CSS-парсер.
    """
    domain = "https://anextour.ru"
    source = "anextour.ru"
    promotions = parse_promotion_settings(
        url=f"{domain}/",
        domain=domain,
        source=source,
    )

    if not promotions:
        promotions = parse_website(
            url=f"{domain}/actions",
            item_selector=".promo-item, .action-card, .promo-card",
            title_selector=".promo-item__title, .action-card__title, h3, h2",
            link_selector="a",
            domain=domain,
        )

    if not promotions:
        try:
            page_html = fetch_page(f"{domain}/actions")
            for match in re.finditer(
                r'"title":"([^"]{8,180})"[\s\S]{0,500}?"slugFull":"([^"]+)"',
                page_html,
            ):
                title = match.group(1).strip()
                link = normalize_link(match.group(2).strip(), domain, f"{domain}/actions")
                promotions.append({
                    'title': title,
                    'link': link,
                    'source': source,
                })
        except Exception as exc:
            logger.error("Ошибка резервного парсинга Anex: %s", exc)

    if not promotions:
        logger.warning(
            "Anex Tour: акции загружаются через JavaScript. "
            "Данные могут быть недоступны без браузерного рендеринга."
        )
    return promotions


def parse_sunmar():
    return parse_promotion_settings(
        url="https://www.sunmar.ru/info-actions/",
        domain="https://www.sunmar.ru",
        source="www.sunmar.ru",
    )


def parse_pegast():
    return parse_pegast_news(
        url="https://pegast.ru/news",
        domain="https://pegast.ru",
        source="pegast.ru",
    )


def parse_funsun():
    return parse_elementor_posts(
        url="https://fstravel.asia/akczii/",
        domain="https://fstravel.asia",
        source="fstravel.asia",
    )


def collect_all_promotions():
    """Запускает все парсеры и объединяет результаты."""
    all_promotions = []
    parsers = [
        parse_coral,
        parse_anex,
        parse_sunmar,
        parse_biblioglobus,
        parse_pegast,
        parse_funsun,
    ]
    for parser in parsers:
        try:
            promotions = parser()
            all_promotions.extend(promotions)
            logger.info("Парсер %s вернул %s предложений", parser.__name__, len(promotions))
        except Exception as exc:
            logger.error("Ошибка в парсере %s: %s", parser.__name__, exc)
    return all_promotions
