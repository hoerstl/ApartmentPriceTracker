from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime as dt
import re
import pandas as pd
from selenium.webdriver.chrome.options import Options







def getApartmentListingData(Price, Apartment):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options) # Put the path to your headless shell in PATH
    
    driver.get("https://galatynstationrichardson.com/floorplans/")

    acceptCookiesButton = WebDriverWait(driver, 500).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".cookie-banner__button.cookie-banner__button--accept"))
    )
    driver.execute_script("arguments[0].click();", acceptCookiesButton)


    prices = []
    apts = []

    for i in range(5):
        floorButton = WebDriverWait(driver, 500).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'.swiper-wrapper'))
        )

        floorButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'[aria-label|="Floor {i}"]'))
        )
        driver.execute_script("arguments[0].click();", floorButton)
        try:
            apartmentCards = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".jd-fp-card-info.jd-fp-card-info--y-adaptive.jd-fp-card-info--small-text"))
            )
        except TimeoutException as e:
            apartmentCards = []
            print(f"Timeout occurred when trying to find floor cards for floor {i}.")
        
        for aptCard in apartmentCards:
            priceData = {}
            text = aptCard.text

            priceData["date"] = dt.now().replace(second=0, microsecond=0)
            priceData["apt"] = int(re.search(r"#(\d+)", text)[1])
            priceData["price"] = int("".join(re.search(r"Starting at \$(.*)", text)[1].split(",")))

            if not (Apartment["apt"] == priceData["apt"]).any():
                aptData = {
                    "apt": int(priceData["apt"]),
                    "beds": int(re.search(r"(\d+) bed", text)[1]),
                    "bath": int(re.search(r"(\d+) bath", text)[1]),
                    "sqft": int(re.search(r"(\d+) sq. ft.", text)[1]),
                }
                apts.append(aptData)


            prices.append(priceData)

    assert prices
    newPrices = pd.DataFrame(prices)
    newApts = pd.DataFrame(apts)

    driver.close()
    return newPrices, newApts


if __name__ == "__main__":
    data = pd.read_excel("./Galatyn Station.xlsx", sheet_name=None)
    Price = data["Price"]
    Apartment = data["Apartment"]

    Price.sort_values("date", ascending=False)
    pd.Timedelta(hours=3)
    lastScanTime = pd.to_datetime(Price.loc[0, 'date']) if len(Price) > 0 else dt(1, 1, 1)
    timeSinceLastScan = dt.now() - lastScanTime

    getDataInterval = pd.Timedelta(hours=3, minutes=59)
    
    if timeSinceLastScan > getDataInterval:
        print("Getting new data from Galatyn Station's website...")
        newPrices, newApts = getApartmentListingData(Price, Apartment)
        Price = pd.concat([Price, newPrices], ignore_index=True)
        Apartment = pd.concat([Apartment, newApts])
        while True:
            output = "./Galatyn Station.xlsx"
            try:
                with pd.ExcelWriter(output, engine='openpyxl', mode='w') as writer:
                    Price.to_excel(writer, sheet_name='Price', index=False)
                    Apartment.to_excel(writer, sheet_name='Apartment', index=False)
                break
            except PermissionError:
                input(f"Couldn't save {output}. Please close the file and try again.")
        print("Data retrived and saved successfully!")
    else:
        print(f"Data already gathered for this interval. Will collect again at {lastScanTime+getDataInterval+pd.Timedelta(minutes=1)}")