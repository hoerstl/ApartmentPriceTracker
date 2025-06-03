import pandas as pd
from datetime import datetime as dt
import logging
import matplotlib as plt
from galatynStationApts import getApartmentListingData

forceCheckPrices = False

def displayApartmentLineGraph(Price, Apartment):
    plt.plot(x, y1, label='Line 1')
    plt.plot(x, y2, label='Line 2')
    plt.plot(x, y3, label='Line 3')

    # Add labels and legend
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Multiple Line Graph")
    plt.legend()

    # Show plot
    plt.show()




def main():
    global forceCheckPrices
    logger = logging.getLogger('selenium')
    logger.addHandler(logging.FileHandler("./seleniumLog.txt"))

    data = pd.read_excel("./Galatyn Station.xlsx", sheet_name=None)
    Price = data["Price"]
    Apartment = data["Apartment"]

    Price.sort_values("date", ascending=False)
    pd.Timedelta(hours=3)
    lastScanTime = pd.to_datetime(Price.loc[0, 'date']) if len(Price) > 0 else dt(1, 1, 1)
    timeSinceLastScan = dt.now() - lastScanTime

    getDataInterval = pd.Timedelta(hours=3, minutes=59)
    
    if timeSinceLastScan > getDataInterval or forceCheckPrices:
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


    # displayApartmentLineGraph()


if __name__ == "__main__":
    main()

