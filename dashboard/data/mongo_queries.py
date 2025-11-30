from datetime import date
from pymongo import MongoClient
import pandas as pd
import json

client = MongoClient("mongodb://localhost:27017")
db = client["trips_db"]
col = db["fhvhv_trips_2021-10"]

date_today = date.today()


def aggregate_to_json(pipeline, output_file, batch_size=100000):
    """Helper function to aggregate and save to JSON file in batches"""
    cursor = col.aggregate(pipeline, allowDiskUse=True) 
    count = 0
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("[\n") 
        first = True
        for doc in cursor:
            if not first:
                f.write(",\n")  
            else:
                first = False
            json.dump(doc, f, ensure_ascii=False)
            count += 1
            if count % batch_size == 0:
                print(f"{count} documents processed...")
        f.write("\n]")
    print(f"JSON file saved: {output_file}")


###### Basic statistics ######
def get_total_trips():
    """Return the total number of trips in the collection."""
    total_trips = col.count_documents({})
    return total_trips / 1_000_000

def get_size_of_collection():
    """Return the size of the collection in bytes"""
    stats = db.command("collStats", "fhvhv_trips_2021-10")
    size_bytes = stats.get("size", 0)
    size_gb = size_bytes / (1024 ** 3)
    return size_gb

def get_average_trip_distance():
    """Return the average trip distance."""
    pipeline = [
        {"$group": {"_id": None, "avgDistance": {"$avg": "$trip_miles"}}}
    ]
    result = list(col.aggregate(pipeline))
    return result[0]["avgDistance"] if result else 0

def get_average_trip_time():
    """Return the average trip time in minutes."""
    pipeline = [
        {"$group": {"_id": None, "avgTime": {"$avg": "$trip_time"}}}
    ]
    result = list(col.aggregate(pipeline))
    return result[0]["avgTime"] if result else 0

def get_company_count():
    """Return the number of unique companies."""
    return len(col.distinct("hvfhs_license_num"))

def cet_company_num():
    """Return the name of the company ."""
    return col.distinct("hvfhs_license_num")

###### DataFrames for visualizations ######
get_trips_per_day_by_company = [
        {
            "$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$pickup_datetime"}},
                    "company": "$hvfhs_license_num"
                },
                "tripCount": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "Date": "$_id.date",
                "Company": "$_id.company",
                "Trips": "$tripCount"
            }
        },
        {"$sort": {"Date": 1, "Company": 1}}
    ]
aggregate_to_json(get_trips_per_day_by_company, f"dashboard/data/historical_data_json/trips_per_day_by_company_{date_today}.json")

"""total trip distance per day."""
get_trips_distance_total_by_day = [
    
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$pickup_datetime"}},
                "avgDistance": {"$avg": "$trip_miles"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "Date": "$_id",
                "AvgDistance": "$avgDistance"
            }
        },
        {"$sort": {"Date": 1}}
    ]
aggregate_to_json(get_trips_distance_total_by_day, f"dashboard/data/historical_data_json/trips_distance_total_by_day_{date_today}.json")

""" total trip distance and time per company.""" 
get_trips_distance_time_by_company = [
        {
            "$group": {
                "_id": "$hvfhs_license_num",
                "avgDistance": {"$avg": "$trip_miles"},
                "avgTime": {"$avg": "$trip_time"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "Company": "$_id",
                "AvgDistance": "$avgDistance",
                "AvgTime": "$avgTime"
            }
        },
        {"$sort": {"Company": 1}}
    ]  
aggregate_to_json(get_trips_distance_time_by_company, f"dashboard/data/historical_data_json/trips_distance_time_by_company_{date_today}.json")  

"""total profit per company."""
total_profit_by_company = [
        {
            "$project": {
                "hvfhs_license_num": 1,
                "profit_company": {
                    "$subtract": [
                        {
                            "$add": [
                                "$base_passenger_fare",
                                "$tolls",
                                "$bcf",
                                "$sales_tax",
                                "$congestion_surcharge",
                                "$airport_fee",
                                "$tips"
                            ]
                        },
                        "$driver_pay"
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$hvfhs_license_num",
                "total_profit": { "$sum": "$profit_company" },
                "avg_profit": { "$avg": "$profit_company" },
                "trips": { "$sum": 1 }
            }
        },
        { "$sort": { "total_profit": -1 } }
    ]

aggregate_to_json(total_profit_by_company, f"dashboard/data/historical_data_json/total_profit_by_company_{date_today}.json")

""" total profit per company."""
Average_Price_driver_company = [
    {"$group" : {"_id": "$hvfhs_license_num" , "AvgDriverPay": {"$avg" : "$driver_pay"}}}
]

aggregate_to_json(Average_Price_driver_company, f"dashboard/data/historical_data_json/Average_Price_driver_company_{date_today}.json")

"""pickup and dropoff location IDs for all trips."""
get_trips_locations = [
    {
        "$group": {
            "_id": {
                "PULocationID": "$PULocationID",
                "DOLocationID": "$DOLocationID"
            },
            "tripCount": {"$sum": 1}
        }
    },
    {
        "$sort": {"tripCount": -1}  
    },
    {
        "$limit": 5000  
    },
    {
        "$project": {
            "_id": 0,
            "PULocationID": "$_id.PULocationID",
            "DOLocationID": "$_id.DOLocationID",
            "tripCount": 1
        }
    }
]
aggregate_to_json(get_trips_locations, f"dashboard/data/historical_data_json/trips_locations_{date_today}.json")

def load_json_data():
    total_trips = get_total_trips()
    document_size = get_size_of_collection()
    avg_distance = get_average_trip_distance()
    avg_time = get_average_trip_time()
    company_count = get_company_count()
    company_num = cet_company_num()
    # data_trips_per_day_by_company = get_trips_per_day_by_company()
    # distance_total_by_day = get_trips_distance_total_by_day()
    # trips_distance_time_by_company = get_trips_distance_time_by_company()
    # total_profit = total_profit_by_company()
    # prive_drive=Average_Price_driver_company()
    # trips_locations = get_trips_locations()
    cart_visualization = {
        "total_trips": total_trips,
        "document_size": document_size,
        "avg_distance": avg_distance,
        "avg_time": avg_time,
        "company_count": company_count
     }
    # data_visualisation = {
    #     "company_num": company_num,
    #     "data_trips_per_day_by_company": data_trips_per_day_by_company.to_dict(orient="records"),
    #     "distance_total_by_day": distance_total_by_day.to_dict(orient="records"),
    #     "trips_distance_time_by_company": trips_distance_time_by_company.to_dict(orient="records"),
    #     "total_profit_by_company": total_profit.to_dict(orient="records"),
    #     "prive_drive": prive_drive.to_dict(orient="records"),
    #     "trips_locations": trips_locations.to_dict(orient="records")
    # }
    date_today = date.today()
    with open(f"dashboard/data/historical_data_json/cart_visualization_{date_today}.json", "w", encoding="utf-8") as f:
        json.dump(cart_visualization, f, ensure_ascii=False, indent=4)

    # with open(f"dashboard/data/historical_data_json/data_visualization_{date_today}.json", "w", encoding="utf-8") as f:
    #     json.dump(data_visualisation, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    load_json_data()