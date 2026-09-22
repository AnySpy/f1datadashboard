from requests import get
from re import compile
from bs4 import BeautifulSoup, Tag
from requests_ratelimiter import LimiterSession

class DriverStatScraper:
    def __init__(self):
        self.session = LimiterSession(per_second=2, per_minute=60)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })

    def fetch_driver_stats(self, driver_name: str) -> dict[str, dict[str, str]]:
        """Gets the stats of the provided driver

        Args:
            driver_name (str): Name of the driver provided in the format "firstname-lastname" (e.g. "max-verstappen")

        Returns:
            dict[str, dict[str, str]]: Two dictionaries: one containing the season stats of the driver and another containing the career stats of the driver.
        """
        r = self.session.get(f"https://www.formula1.com/en/drivers/{driver_name}")

        if r.status_code != 200:
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

    def _parse_container_stats(self, container: Tag | None) -> dict[str, str]:
        if container is None:
            return {}

        data = {}

        items = container.find_all("div", class_=compile(r"^DataGrid-module_item"))
        for item in items:
            # ? Titles are stored in the class "DataGrid-module_title" and values are stored in "DataGrid-module_description"
            # ? This has to use regex because of PyLance. We probably *could* have just passed a string to `class_` but I don't want to fight PyLance.
            title_elem = item.find("dt", class_=compile(r"^DataGrid-module_title"))
            value_elem = item.find("dd", class_=compile(r"^DataGrid-module_description"))

            # ? Can return None and PyLance gets upset if we don't have this check
            if title_elem and value_elem:
                title = title_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)

                data[title] = value

        return data

def _main():
    name = "max-verstappen"
    scraper = DriverStatScraper()

    results = scraper.fetch_driver_stats(name)

    print(results)

    return 0

if __name__ == '__main__':
    _main()