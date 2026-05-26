from turtle import home
import matplotlib.pyplot as plt
import os

def altitude_chart(aircraft_list):
    altitudes = [a['altitude'] for a in aircraft_list if a['altitude'] is not None and a['altitude'] > 0]
    
    if not altitudes:   
        return home

    plt.figure(figsize=(8, 4))
    plt.hist(altitudes, bins=15, color='skyblue', edgecolor='black')
    plt.title("Altitude Distribution of Nearby Aircraft")
    plt.xlabel("Altitude (meeters)")
    plt.ylabel("Number of Aircraft")   
    plt.grid(True, alpha=0.3)
    os.makedirs("static", exist_ok=True)
    path = "static/altitude_hist.png"
    plt.savefig(path)
    plt.close()
        
    return path