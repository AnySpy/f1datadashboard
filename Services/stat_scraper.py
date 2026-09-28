from re import compile
from bs4 import BeautifulSoup, Tag
from requests_ratelimiter import LimiterSession
import typing


class DriverStatScraper:
    def __init__(self):
        """Generic initialization for the stat scraper. Instantiates a rate-limited session and sets the headers of that session.
        """
        self.session = LimiterSession(per_second=2, per_minute=60)
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )

    def fetch_driver_stats(self, driver_name: str) -> dict[str, dict[str, str]]:
        """Gets the stats of the provided driver

        Args:
            driver_name (str): Name of the driver provided in the format "firstname-lastname" (e.g. "max-verstappen")

        Returns:
            dict[str, dict[str, str]]: Two dictionaries: one containing the season stats of the driver and another containing the career stats of the driver.
        """
        r = self.session.get(f"https://www.formula1.com/en/drivers/{driver_name}")

        if r.status_code != 200 or "drivers" not in r.url:
            return {"seasons": {}, "career": {}}

        soup = BeautifulSoup(r.text, "html.parser")
        driver_stats = {"season": {}, "career": {}}

        # ! This feels very fragile and I'd like to find a better way to do this in the future, but for right now it works so :shrug:
        season_container = soup.find("div", class_=compile(r"^order-1"))
        career_container = soup.find("div", class_=compile(r"^order-3"))

        if season_container:
            driver_stats["season"] = self._parse_container_stats(season_container)
        if career_container:
            driver_stats["career"] = self._parse_container_stats(career_container)

        return driver_stats

    def _fetch_driver_image_url(self, soup: BeautifulSoup) -> str | None:
        """Gets the driver's image URL from the f1 website

        Args:
            soup (BeautifulSoup): A `BeautifulSoup` object that contains the request text and is using the html parser.

        Returns:
            str | None: The URL as a string or `None` if there is no valid URL.
        """
        # ? This uses the fact that there's only one image that contains `media.formula1.com` on the website to grab the driver's image
        img_tag = soup.find("img", src=compile(r"media\.formula1\.com"))

        if img_tag and img_tag.get("src"):
            # ? I hate PyLance. "Waah! Waah! You're returning str when it *could* be List[str]" (it can't)
            # ?     I will not stop using type hinting in Python and am closed to any related suggestions
            return typing.cast(str, img_tag["src"])

        return None

    def fetch_driver_image(self, driver_name: str) -> bytes | None:
        """Gets the bytestream of the driver's image from the f1 website

        Args:
            driver_name (str): Name of the driver provided in the format "firstname-lastname" (e.g. "max-verstappen")

        Returns:
            bytes | None: The bytestream of the image or `None` if there is no valid image found.
        """
        r = self.session.get(f"https://www.formula1.com/en/drivers/{driver_name}")
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        img_url = self._fetch_driver_image_url(soup)
        if not img_url:
            return None

        img_response = self.session.get(img_url)
        if img_response.status_code == 200:
            return img_response.content

        return None

    def _parse_container_stats(self, container: Tag | None) -> dict[str, str]:
        """Helper function for `fetch_driver_stats()`. Creates the internal dictionaries of the nested dict structure.

        Args:
            container (Tag | None): A collection of Tags found by the `soup.find()` method.

        Returns:
            dict[str, str]: A dictionary containing the title of the stat as the key and the value of the stat as the value.
        """
        if container is None:
            return {}

        data = {}

        items = container.find_all("div", class_=compile(r"^DataGrid-module_item"))
        for item in items:
            # ? Titles are stored in the class "DataGrid-module_title" and values are stored in "DataGrid-module_description"
            # ? This has to use regex because of PyLance. We probably *could* have just passed a string to `class_` but I don't want to fight PyLance.
            title_elem = item.find("dt", class_=compile(r"^DataGrid-module_title"))
            value_elem = item.find(
                "dd", class_=compile(r"^DataGrid-module_description")
            )

            # ? Can return None and PyLance gets upset if we don't have this check
            if title_elem and value_elem:
                title = title_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)

                data[title] = value

        return data

    def fetch_driver_bio(self, driver_name: str) -> str:
        """Returns the driver's biography from the F1 website

        Args:
            driver_name (str): Name of the driver provided in the format "firstname-lastname" (e.g. "max-verstappen")

        Returns:
            str: The biography of the driver as a string.
        """
        # ? Trying something new with scraping stats. We'll see if this is less fragile.
        r = self.session.get(f"https://www.formula1.com/en/drivers/{driver_name}")

        if r.status_code != 200:
            return "Biography Not Available."

        soup = BeautifulSoup(r.text, "html.parser")

        bio_heading = soup.find(
            lambda tag: (
                tag.name in ["h2", "h3", "h4", "p"]
                and "BIOGRAPHY" in tag.get_text().upper()
            )
        )

        if not bio_heading:
            return "Biography Not Available."

        # ? We have to sequentially move up because of all the wrappings of divs.
        container = bio_heading.parent
        while container and not container.find_all("p"):
            container = container.parent

        assert container is not None
        paragraphs = container.find_all("p")

        bio_text = "\n\n".join(
            p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
        )

        return bio_text if bio_text else "Biography Not Available."


def _main():
    name = "max-verstappen"
    scraper = DriverStatScraper()

    results = scraper.fetch_driver_image(name)

    print(results)

    return 0


if __name__ == "__main__":
    _main()
