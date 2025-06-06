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
        if Apartment[Apartment["apt"] == apt]["beds"].values[0] == 1:
            plt.plot(apt_prices["date"], apt_prices["price"], marker='o', label=f"Apt {apt}")
        else:
            plt.plot(apt_prices["date"], apt_prices["price"], marker='o', color="red") 



    # Add labels and legend
    plt.xlabel("Time")
    plt.ylabel("Price ($)")
    plt.title("Prices of Apartments at Galatyn Station")

    plt.grid(axis='y', linestyle='--', color='gray', alpha=0.7)


    legend_elements = [
        Line2D([0], [0], color='blue', lw=2, label='1 Bed'),
        Line2D([0], [0], color='red', lw=2, label='2+ Beds')
    ]

    # Add the custom legend
    plt.legend() #handles=legend_elements, title="Bedroom Count"
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

    mostRecentScanTime = pd.to_datetime(Price["date"].max()) if len(Price) > 0 else dt(1, 1, 1)
    timeSinceLastScan = dt.now() - mostRecentScanTime

    getDataInterval = pd.Timedelta(hours=3, minutes=59)
    
    if timeSinceLastScan > getDataInterval or forceCheckPrices:
        print("Getting new data from Galatyn Station's website...")
        newPrices, newApts = getApartmentListingData(Price, Apartment)
        Price = pd.concat([Price, newPrices], ignore_index=True)
        Price = Price.sort_values("date", ascending=False)
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
        mostRecentScanTime = dt.now().replace(second=0, microsecond=0)
        print("Data retrived and saved successfully!")
    else:
        print(f"Data already gathered for this interval. Will collect again at {mostRecentScanTime+getDataInterval+pd.Timedelta(minutes=1)}")



    # Step 2: Filter the Price DataFrame for entries matching the most recent datetime
    mostRecentPriceScan = Price[Price["date"] == mostRecentScanTime]

    # Step 3: Find apartments in the Apartment DataFrame not in the recent prices
    missingApartments = Apartment[~Apartment["apt"].isin(mostRecentPriceScan["apt"])]

    last_prices = (
        Price[Price["apt"].isin(missingApartments["apt"])]
        .sort_values("date")
        .groupby("apt")
        .last()[["price", "date"]]
        .reset_index()
    )

    # Merge missing apartments with their last recorded prices
    missingApartmentsWithPrices = pd.merge(
        missingApartments,
        last_prices,
        how="left",
        on="apt"
    ).sort_values("date", ascending=False).reset_index()

    print(f"Apartments: {list(missingApartmentsWithPrices['apt'])} \nHave been sold or taken off the market at the following prices at these dates:\n{missingApartmentsWithPrices[['apt', 'price', 'date']]}")


    displayApartmentLineGraph(Price, Apartment)



if __name__ == "__main__":
    main()

