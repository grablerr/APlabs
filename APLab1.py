from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

import time, os


class ReviewsCard:
    def __init__(self, reviews_source):
        self.reviews_source = reviews_source

    def get_book_name(self):
        try: return self.reviews_source.find_element("css selector", "a.lenta-card__book-title").text
        except NoSuchElementException: return "Книга не имеет названия"

    def get_book_author(self):
        try: return self.reviews_source.find_element("css selector", "a.lenta-card__author").text
        except NoSuchElementException: return "Автор не указан"

    def get_count_star(self):
        try: return self.reviews_source.find_element("css selector", "span.lenta-card__mymark").text
        except NoSuchElementException: return "Без рейтинга"

    def get_reviews_text(self):
        try: return self.reviews_source.find_element("css selector", "div#lenta-card__text-review-full").text
        except NoSuchElementException :return self.reviews_source.find_element("css selector", "div#lenta-card__text-review-escaped").text

    def get_reviews_spoiler_text(self):
        try:
            text = self.reviews_source.find_element("css selector", "div#lenta-card__text-review-full").text
            spoiler = self.reviews_source.find_element("css selector", "div.spoiler-text").text
            text_spoiler = text.replace('спойлер', spoiler)
            return text_spoiler
        except NoSuchElementException :
            text = self.reviews_source.find_element("css selector", "div#lenta-card__text-review-escaped").text
            spoiler = self.reviews_source.find_element("css selector", "div.spoiler-text").text
            text_spoiler = text.replace('спойлер', spoiler)
            return text_spoiler


