import matplotlib
matplotlib.use('Agg')  # for headless environments

from flask import Flask, render_template, request, redirect, url_for
from apis import geocode, load_airports, find_nearest_airports, get_live_aircraft
from control_panel import (
    save_search, get_searches, delete_search,
    save_bookmark, get_bookmarks, delete_bookmark,
    save_snapshots, get_snapshots, get_distinct_timestamps, compare_traffic
)
from map_utils import make_map
from charts import altitude_chart
import db

app = Flask(__name__)
db.create_tables()  # ensure tables exist

@app.route('/')
def index():
    return render_template('index.html', map_html=None, chart_path=None, aircraft_data=None)

@app.route('/search', methods=['POST'])
def search():
    city = request.form.get('city')
    lat, lon, city_name = geocode(city)
    if lat is None:
        return f"City '{city}' not found. <a href='/'>Go back</a>"

    # Save search to history
    save_search(city_name, lat, lon)

    # Load airports and find nearest
    all_airports = load_airports()
    nearby = find_nearest_airports(lat, lon, all_airports, limit=8)

    # Get live aircraft in bounding box (approx 0.5 deg)
    bbox = 0.5
    min_lat = lat - bbox
    max_lat = lat + bbox
    min_lon = lon - bbox
    max_lon = lon + bbox
    aircraft = get_live_aircraft(min_lat, min_lon, max_lat, max_lon)

    # Save snapshot for later comparison
    save_snapshots(aircraft)

    # Generate map
    map_html = make_map(lat, lon, nearby, aircraft)

    # Generate altitude chart
    chart_path = altitude_chart(aircraft)

    return render_template('index.html',
                           map_html=map_html,
                           chart=chart_path,
                           aircraft_data=aircraft,
                           nearby_count=len(nearby))

@app.route('/history')
def history():
    searches = get_searches()
    return render_template('history.html', searches=searches)

@app.route('/delete/<int:search_id>')
def delete(search_id):
    delete_search(search_id)
    return redirect(url_for('history'))

@app.route('/control_panel')
def control_panel():
    bookmarks = get_bookmarks()
    snapshots = get_snapshots(20)
    timestamps = get_distinct_timestamps()
    return render_template('control.html', bookmarked=bookmarks, snapshots=snapshots, timestamps=timestamps, comparison=None)

@app.route('/delete_bookmark/<int:bookmark_id>')
def delete_bookmark_route(bookmark_id):
    delete_bookmark(bookmark_id)
    return redirect(url_for('control_panel'))

@app.route('/compare', methods=['POST'])
def compare():
    previous_ts = request.form.get('previous_timestamp')
    if not previous_ts:
        return redirect(url_for('control_panel'))
    
    return "Please perform a search first, then use comparison. <a href='/'>Go to search</a>"
if __name__ == '__main__':
    app.run(debug=True, port=5000)