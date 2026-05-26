import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, render_template_string, redirect, url_for
from apis import geocode, find_nearest_airports, load_airports, get_live_aircraft
from control_panel import save_search, get_searches, delete_search, save_bookmark, get_bookmarks, delete_bookmark, save_snapshot, get_distinct_timestamps, compare_traffic

from map_utils import make_map
from charts import altitude_chart
import db

@app.route('/')
def index():
    return render_template_string('''
        <h2>Live Aircraft Explorer</h2>
        <form action="/search" method="post">
            <input name="city" placeholder="City name" required>
            <button type="submit">Search</button>
        </form>
        <br>
        <a href="/history">View Search History</a>
    ''')

@app.route('/search', methods=['POST'])
def search():
    city = request.form.get('city')
    lat, lon, city_name = geocode(city)
    if lat is None:
        return f'City "{city}" not found. <a href="/">Try again</a>'
    
    save_search(city_name, lat, lon)

    all_airports = load_airports()
    nearby = find_nearest_airports(lat, lon, all_airports, limit=8)

    # Adaptive bounding box: 0.5 degrees at equator ~55km, shrink at higher latitudes
    bbox_size = 0.5  # Default value, can be adjusted or made user-configurable
    min_lat = lat - bbox_size
    max_lat = lat + bbox_size
    min_lon = lon - bbox_size / max(1, abs(lat)/90)  # Adjust for latitude distortion
    max_lon = lon + bbox_size / max(1, abs(lat)/90)
    aircraft = get_live_aircraft(min_lat, min_lon, max_lat, max_lon)

    map_html = stub_map(lat, lon, nearby, aircraft)
    chart_html = stub_chart(aircraft)

    return f'''
    <h3>Results for {city_name}</h3>
    <p>Nearby airports: {len(nearby)} | Live aircraft: {len(aircraft)}</p>
    {map_html}
    {chart_html}
    <br>
    <a href="/">New search</a> | <a href="/history">History</a>
    '''

@app.route('/history')
def history():
    rows = get_search_history(limit=30)
    if not rows:
        return 'No searches yet. <a href="/">Go search</a>'
    template = '''
    <h3>Search History</h3>
    <ul>
    {% for r in rows %}
        <li>{{ r.city }} at {{ r.search_time }}
            <a href="{{ url_for('delete_record', search_id=r.id) }}" onclick="return confirm('Delete?')">[delete]</a>
        </li>
    {% endfor %}
    </ul>
    <a href="/">Back</a>
    '''
    return render_template_string(template, rows=rows)

@app.route('/delete/<int:search_id>')
def delete_record(search_id):
    delete_search(search_id)
    return redirect(url_for('history'))

def stub_map(lat, lon, nearby, aircraft):
    # Placeholder implementation for map rendering
    return f"<div>Map showing {len(nearby)} airports and {len(aircraft)} aircraft near ({lat}, {lon})</div>"

def stub_chart(aircraft):

    aircraft_count = len(aircraft)

    plt.figure(figsize=(5, 4))

    plt.bar(["Aircraft"], [aircraft_count])

    plt.title("Live Aircraft Count")

    plt.ylabel("Number of Aircraft")

    chart_path = "static/chart.png"

    plt.savefig(chart_path)

    plt.close()

    return f'<img src="/static/chart.png" width="500">'

if __name__ == '__main__':
    app.run(debug=True, port=5000)