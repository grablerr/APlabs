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


def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')

    service = Service(executable_path="web_driver\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    try:
        for page_number in range(1, 401):
            driver.get(url=f"https://www.livelib.ru/reviews/~{page_number}#reviews")
            time.sleep(3.5)
            try: driver.find_element("css selector", "div.btn-cookies-agree").click()
            except NoSuchElementException: pass
            time.sleep(0.5)

            read_more_buttons = driver.find_elements("css selector", "a.read-more__link")
            for read_more_button in read_more_buttons:
                try:
                    btn_close = driver.find_element("css selector", "a.btn-close")
                    driver.execute_script("arguments[0].click();", btn_close)
                except NoSuchElementException:
                    driver.execute_script("arguments[0].scrollIntoView();", read_more_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", read_more_button)

            spoiler_buttons = driver.find_elements("css selector", "a.spoiler-open")
            for spoiler_button in spoiler_buttons:
                try:
                    btn_close = driver.find_element("css selector", "a.btn-close")
                    driver.execute_script("arguments[0].click();", btn_close)
                except NoSuchElementException:
                    driver.execute_script("arguments[0].scrollIntoView();", spoiler_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", spoiler_button)


            reviews_cards = driver.find_elements("css selector", "article.review-card")

            for reviews_card in reviews_cards:
                reviews_info = ReviewsCard(reviews_card)
                try:
                    reviews_card.find_element("css selector", "div.spoiler-text")

                    reviews_data = {
                        "name": reviews_info.get_book_name(),
                        "author": reviews_info.get_book_author(),
                        "count_star": reviews_info.get_count_star(),
                        "reviews": reviews_info.get_reviews_spoiler_text(),
                    }

                except NoSuchElementException:

                    reviews_data = {
                        "name": reviews_info.get_book_name(),
                        "author": reviews_info.get_book_author(),
                        "count_star": reviews_info.get_count_star(),
                        "reviews": reviews_info.get_reviews_text(),
                    }


                print(reviews_data)

    except Exception as error:
        print(error)
    finally:
        driver.close()
        driver.quit()

if __name__ == "__main__":
    main()