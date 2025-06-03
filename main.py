import pandas as pd
from datetime import datetime as dt
import logging
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from galatynStationApts import getApartmentListingData

forceCheckPrices = False

def displayApartmentLineGraph(Price, Apartment):
    Price["date"] = pd.to_datetime(Price["date"])

    plt.figure(figsize=(12, 6))

    # Plot each apartment individually
    for apt in Apartment["apt"].unique():
        apt_prices = Price[Price["apt"] == apt].sort_values("date")
        plt.plot(apt_prices["date"], apt_prices["price"], label=f"Apt {apt}", color="blue" if Apartment[Apartment["apt"] == apt]["beds"].values[0] == 1 else "red")



    # Add labels and legend
    plt.xlabel("Time")
    plt.ylabel("Price ($)")
    plt.title("Prices of Apartments at Galatyn Station")

    legend_elements = [
        Line2D([0], [0], color='blue', lw=2, label='1 Bed'),
        Line2D([0], [0], color='red', lw=2, label='2+ Beds')
    ]

    # Add the custom legend
    plt.legend(handles=legend_elements, title="Bedroom Count")
    plt.xticks(rotation=45)

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


    displayApartmentLineGraph(Price, Apartment)


if __name__ == "__main__":
    main()

