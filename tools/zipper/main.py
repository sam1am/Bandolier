from flask import Flask, request, send_from_directory, jsonify
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder='static')

# Replace with your actual token
token = os.getenv("INFLUXDB_TOKEN")
org = "Self"
bucket = "lifelog"

client = InfluxDBClient(url="http://localhost:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/add_to_timeline', methods=['POST'])
def add_to_timeline():
    # Extract data from the request
    data = request.json

    # Create a new entry
    point = Point("timeline").field("value", data.get('value')).tag("tag", data.get('tag'))
    print(f"Saving data: {data.get('value')} with tag {data.get('tag')}")

    # Write the point to the database
    write_api.write(bucket=bucket, org=org, record=point)

    return 'Success!', 200

@app.route('/get_timeline', methods=['GET'])
def get_timeline():
    query = f'from(bucket: "{bucket}") |> range(start: -1d) |> filter(fn: (r) => r["_measurement"] == "timeline") |> limit(n: 50)'
    result = query_api.query(query, org=org)

    timeline = []
    for table in result:
        for record in table.records:
            timeline.append({
                'timestamp': record.get_time().isoformat(),
                'type': record.values.get('tag'),    # updated 'type' to 'tag'
                'value': record.values.get('_value') # updated 'value' to '_value'
            })

    return jsonify(timeline)


    return jsonify(timeline)

# @app.route('/delete_from_timeline', methods=['POST'])
# def delete_from_timeline():
#     # Extract data from the request
#     data = request.json

#     # Delete the entry
#     query = f'delete from "timeline" where time = \'{data.get("timestamp")}\''
#     result = query_api.query(query, org=org)

#     return 'Success!', 200

if __name__ == '__main__':
    app.run(debug=True, port=5004)
