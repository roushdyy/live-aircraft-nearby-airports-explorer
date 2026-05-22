import matplotlib.pyplot as plt


def create_chart(aircraft_count):

    hours = ["Now"]
    values = [aircraft_count]

    plt.figure(figsize=(5, 4))

    plt.bar(hours, values)

    plt.title("Aircraft Count")

    plt.xlabel("Time")

    plt.ylabel("Aircraft")

    chart_path = "static/chart.png"

    plt.savefig(chart_path)

    plt.close()

    return chart_path