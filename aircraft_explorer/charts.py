import matplotlib.pyplot as plt
import os
import time


def altitude_chart(aircraft_list):

    if not aircraft_list:
        aircraft_list = []

    callsigns = [a.get("callsign", "N/A") for a in aircraft_list]
    altitudes = [a.get("altitude", 0) for a in aircraft_list]

    if not callsigns:
        callsigns = ["No flights"]
        altitudes = [0]

    plt.figure(figsize=(8, 4))
    plt.bar(callsigns, altitudes, color="skyblue")

    plt.title("Aircraft Altitudes")
    plt.xlabel("Callsign")
    plt.ylabel("Altitude")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    chart_path = os.path.join(static_dir, "chart.png")

    plt.savefig(chart_path)
    plt.close()

    return f"/static/chart.png?{int(time.time())}"