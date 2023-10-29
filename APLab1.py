from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

import time, os, json

start_page = 1
last_page = 401


class ReviewsCard:
    def __init__(self, reviews_source):
        self.reviews_source = reviews_source

    def get_book_name(self):
        try: return self.reviews_source.find_element("css selector", "a.lenta-card__book-title").text
        except NoSuchElementException: return "Книга не имеет названия"

    def get_book_author(self):
        try: return self.reviews_source.find_element("css selector", "a.lenta-card__author").text
        except NoSuchElementException:return "Автор не указан"

    def get_count_star(self):
        try: return self.reviews_source.find_element("css selector", "span.lenta-card__mymark").text
        except NoSuchElementException: return "Без рейтинга"

    def get_reviews_text(self):
        try: return self.reviews_source.find_element("css selector", "div#lenta-card__text-review-full").text
        except NoSuchElementException: return self.reviews_source.find_element("css selector", "div#lenta-card__text-review-escaped").text

    def get_reviews_spoiler_text(self):
        try:
            text = self.reviews_source.find_element("css selector", "div#lenta-card__text-review-full").text
            spoiler = self.reviews_source.find_element("css selector", "div.spoiler-text").text
            text_spoiler = text.replace('спойлер', spoiler)
            return text_spoiler
        except NoSuchElementException:
            text = self.reviews_source.find_element("css selector", "div#lenta-card__text-review-escaped").text
            spoiler = self.reviews_source.find_element("css selector", "div.spoiler-text").text
            text_spoiler = text.replace('спойлер', spoiler)
            return text_spoiler


class ReviewDataProcessor:
    def __init__(self, reviews_data):
        self.reviews_data = reviews_data
        self.main_folder = "dataset"

    def process(self):
        book_name = self.reviews_data["name"].replace(" ", "_")

        count_star = self.reviews_data["count_star"]
        if   (count_star != 'Без рейтинга') and (0 < float(count_star) <= 1):  star_folder = os.path.join(self.main_folder, "1")
        elif (count_star != 'Без рейтинга') and (1 < float(count_star) <= 2): star_folder = os.path.join(self.main_folder, "2")
        elif (count_star != 'Без рейтинга') and (2 < float(count_star) <= 3): star_folder = os.path.join(self.main_folder, "3")
        elif (count_star != 'Без рейтинга') and (3 < float(count_star) <= 4): star_folder = os.path.join(self.main_folder, "4")
        elif (count_star != 'Без рейтинга') and (4 < float(count_star) <= 5): star_folder = os.path.join(self.main_folder, "5")
        else: star_folder = os.path.join(self.main_folder, "other")

        os.makedirs(star_folder, exist_ok=True)

        existing_files = os.listdir(star_folder)
        for existing_file in existing_files:
            if existing_file.endswith(".txt"):
                existing_file_path = os.path.join(star_folder, existing_file)
                with open(existing_file_path, "r", encoding="utf-8") as file:
                    existing_data = file.read()
                if existing_data == self.reviews_data["author"] + "\n" + self.reviews_data["name"] + "\n" + \
                        self.reviews_data["reviews"]:
                    return

        existing_files = [f for f in os.listdir(star_folder) if f.endswith(".txt")]
        next_number = len(existing_files)
        new_file_name = f"{next_number:04d}.txt"
        new_file_path = os.path.join(star_folder, new_file_name)
        with open(new_file_path, "w", encoding="utf-8") as file:
            file.write(self.reviews_data["author"] + "\n")
            file.write(self.reviews_data["count_star"] + "\n")
            file.write(self.reviews_data["name"] + "\n")
            file.write(self.reviews_data["reviews"])

    def save_page_info(self, current_page):
        page_info = {
            "start_page": start_page,
            "last_page": last_page,
            "current_page": current_page
        }
        with open('page_info.json', 'w') as json_file:
            json.dump(page_info, json_file)

    def load_page_info(self):
        try:
            with open('page_info.json', 'r') as json_file:
                page_info = json.load(json_file)
                return page_info["current_page"]
        except FileNotFoundError:
            return start_page



def main():
    global start_page, last_page
    start_page = 1
    last_page = 401

    # Настройка браузера
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')

    # Инициализация драйвера
    service = Service(executable_path="web_driver\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        processor = ReviewDataProcessor({})
        current_page = processor.load_page_info()
        for page_number in range(current_page, last_page):
            driver.get(url=f"https://www.livelib.ru/reviews/~{page_number}#reviews")
            time.sleep(4)
            try: driver.find_element("css selector", "div.btn-cookies-agree").click()
            except NoSuchElementException: pass
            time.sleep(2)

            read_more_buttons = driver.find_elements("css selector", "a.read-more__link")
            for read_more_button in read_more_buttons:
                try:
                    btn_close = driver.find_element("css selector", "a.btn-close")
                    driver.execute_script("arguments[0].click();", btn_close)
                except NoSuchElementException:
                    driver.execute_script("arguments[0].scrollIntoView();", read_more_button)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", read_more_button)

            spoiler_buttons = driver.find_elements("css selector", "a.spoiler-open")
            for spoiler_button in spoiler_buttons:
                try:
                    btn_close = driver.find_element("css selector", "a.btn-close")
                    driver.execute_script("arguments[0].click();", btn_close)
                except NoSuchElementException:
                    driver.execute_script("arguments[0].scrollIntoView();", spoiler_button)
                    time.sleep(2)
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

                    processor = ReviewDataProcessor(reviews_data)
                    processor.save_page_info(page_number)
                    processor.process()
                except NoSuchElementException:

                    reviews_data = {
                        "name": reviews_info.get_book_name(),
                        "author": reviews_info.get_book_author(),
                        "count_star": reviews_info.get_count_star(),
                        "reviews": reviews_info.get_reviews_text(),
                    }

                    processor = ReviewDataProcessor(reviews_data)
                    processor.save_page_info(page_number+2)
                    processor.process()

                print(reviews_data)

    except Exception as error:
        print(error)
    finally:
        driver.close()
        driver.quit()


if __name__ == "__main__":
    main()
