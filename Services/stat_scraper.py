from requests import get
from re import compile
from bs4 import BeautifulSoup

# Data is stored in class "DataGrid-module_item__[hash]"

def get_stats(driver_name: str) -> dict[str, str]:
    """Gets the stats of the provided driver

    Args:
        driver_name (str): Name of the driver provided in the format "firstname-lastname" (e.g. "max-verstappen")

    Returns:
        dict[str, str]: A dictionary that is formatted as [title, value]
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    r = get(f"https://www.formula1.com/en/drivers/{driver_name}", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    driver_stats = {}

    # ? Elements are stored in the class "DataGrid-module_item__[hash]" 
    items = soup.find_all("div", class_=compile(r"^DataGrid-module_item"))
    for item in items:
        # ? Titles are stored in the class "DataGrid-module_title" and values are stored in "DataGrid-module_description"
        title_elem = item.find("dt", class_=compile(r"^DataGrid-module_title"))
        value_elem = item.find("dd", class_=compile(r"^DataGrid-module_description"))

        # ? Can return None and PyLance gets upset if we don't have this check
        if title_elem and value_elem:
            title = title_elem.get_text(strip=True)
            value = value_elem.get_text(strip=True)

            driver_stats[title] = value

    return driver_stats

def main():
    name = "max-verstappen"
    results = get_stats(name)

    print(results)

    return 0

if __name__ == '__main__':
    main()