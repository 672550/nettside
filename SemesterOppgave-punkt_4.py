import matplotlib
matplotlib.use('TkAgg')  # Bruk en interaktiv backend
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import random
from random import randint

def GenereateRandomYearDataList(intencity: float, seed: int = 0) -> list[int]:
    if seed != 0:
        random.seed(seed)
    centervals = [200, 150, 100, 75, 75, 75, 50, 75, 100, 150, 200, 250, 300]
    centervals = [x * intencity for x in centervals]
    nox = centervals[0]
    inc = True
    noxList = []
    for index in range(1, 366):
        if randint(1, 100) > 50:
            inc = not inc
        center = centervals[int((index - 1) / 30)]
        dx = min(2.0, max(0.5, nox / center))
        nox = nox + randint(1, 5) / dx if inc else nox - randint(1, 5) * dx
        nox = max(10, nox)
        noxList.append(nox)
    return noxList

kron_nox_year = GenereateRandomYearDataList(intencity=1.0, seed=2)
nord_nox_year = GenereateRandomYearDataList(intencity=.3, seed=1)
kalfaret_nox_year = GenereateRandomYearDataList(intencity=0.7, seed=3) #Dette er den nye stasjonen


# Opprett figur og akser
fig = plt.figure(figsize=(13, 6))

axNok = fig.add_axes([0.05, 0.15, 0.40, 0.75])
axBergen = fig.add_axes([0.5, 0.15, 0.5, 0.75])

# Opprett akse for RangeSlider
axSlider = fig.add_axes([0.15, 0.01, 0.7, 0.03])

# Opprett RangeSlider
slider = RangeSlider(
    ax=axSlider,
    label='Dag',
    valmin=1,
    valmax=365,
    valinit=(1, 365),
    valstep=1,
    orientation='horizontal'
)

coordinates_Nordnes = (300, 240)
coordinates_Kronstad = (1150, 1300)
coordinates_Kalfaret = (1000, 655)       # Denne er ny

circle_radius = 35


days_interval = (1, 365)
marked_point = (0, 0)
selected_station = None

def is_inside_circle(circle_center, radius, point):
    dx = circle_center[0] - point[0]
    dy = circle_center[1] - point[1]
    distance = math.hypot(dx, dy)
    return distance <= radius

def on_click(event):
    global marked_point, selected_station
    if event.inaxes == axBergen:
        click_point = (event.xdata, event.ydata)
        print(f"Klikk registrert på koordinater: {click_point}")
        if is_inside_circle(coordinates_Nordnes, circle_radius, click_point):
            selected_station = 'Nordnes'
            print("Nordnes valgt")
        elif is_inside_circle(coordinates_Kronstad, circle_radius, click_point):
            selected_station = 'Kronstad'
            print("Kronstad valgt")
        elif is_inside_circle(coordinates_Kalfaret, circle_radius, click_point):
            selected_station = 'Kalfaret'
            print("Kalfaret valgt")
        else:
            selected_station = None
            marked_point = click_point
        plot_graph()


def CalcPointValue(valN, valK, valKa):
    distNordnes = math.dist(coordinates_Nordnes, marked_point)
    distKronstad = math.dist(coordinates_Kronstad, marked_point)
    distKalfaret = math.dist(coordinates_Kalfaret, marked_point)

    # Unngå divisjon med null
    if distNordnes == 0:
        weightN = 1
        weightK = 0
        weightKa = 0
    elif distKronstad == 0:
        weightN = 0
        weightK = 1
        weightKa = 0
    elif distKalfaret == 0:
        weightN = 0
        weightK = 0
        weightKa = 1
    else:
        weightN = 1 / distNordnes
        weightK = 1 / distKronstad
        weightKa = 1 / distKalfaret
        total_weight = weightN + weightK + weightKa
        weightN /= total_weight
        weightK /= total_weight
        weightKa /= total_weight

    # Beregn NOX-verdi
    val = weightN * valN + weightK * valK + weightKa * valKa

    return val


def draw_circles_stations():
    circle_nordnes = mpatches.Circle(coordinates_Nordnes, circle_radius, color='blue')
    axBergen.add_patch(circle_nordnes)
    circle_kronstad = mpatches.Circle(coordinates_Kronstad, circle_radius, color='red')
    axBergen.add_patch(circle_kronstad)
    circle_kalfaret = mpatches.Circle(coordinates_Kalfaret, circle_radius, color='green')
    axBergen.add_patch(circle_kalfaret)                                 # Denne er ny

def draw_label_and_ticks():
    total_days = days_interval[1] - days_interval[0] + 1
    list_days = np.linspace(days_interval[0], days_interval[1], total_days)
    num_labels = min(12, total_days)
    xticks = np.linspace(days_interval[0], days_interval[1], num_labels)
    xlabels = [f'Dag {int(day)}' for day in xticks]
    axNok.set_xticks(xticks)
    axNok.set_xticklabels(xlabels, rotation=45, ha='right')


def plot_graph():
    axNok.cla()
    axBergen.cla()
    nord_nox = nord_nox_year[days_interval[0]-1:days_interval[1]]
    kron_nox = kron_nox_year[days_interval[0]-1:days_interval[1]]
    kalfaret_nox = kalfaret_nox_year[days_interval[0]-1:days_interval[1]]
    days = len(nord_nox)
    list_days = np.linspace(days_interval[0], days_interval[1], days)

    lines = []
    labels = []

    # Plotter NOX-data
    l1, = axNok.plot(list_days, nord_nox, 'blue')
    l2, = axNok.plot(list_days, kron_nox, 'red')
    l3, = axNok.plot(list_days, kalfaret_nox, 'green')
    lines.extend([l1, l2, l3])
    labels.extend(['Nordnes', 'Kronstad', 'Kalfaret'])

    # Beregn gjennomsnitt for Kronstad (uten å plotte linjen)
    avg_kronstad = np.mean(kron_nox)

    # Håndter markert plass
    if marked_point != (0, 0) and selected_station is None:
        # Beregn og plot NOX for markert plass
        nox_point = [
            CalcPointValue(nord_nox[i], kron_nox[i], kalfaret_nox[i]) for i in range(days)
        ]
        l4, = axNok.plot(list_days, nox_point, 'darkorange')
        lines.append(l4)
        labels.append('Markert plass')
        circle = mpatches.Circle((marked_point[0], marked_point[1]), circle_radius, color='orange')
        axBergen.add_patch(circle)

        # Beregn gjennomsnitt og prosentandel i forhold til Kronstad
        avg_marked = np.mean(nox_point)
        prosent = (avg_marked / avg_kronstad) * 100  # for å bergne gjennomsnitt mot kronstad prosentvis

        # Plott gjennomsnittslinje for markert plass
        axNok.axhline(y=avg_marked, color='gold', linestyle='--')
        lines.append(axNok.lines[-1])
        labels.append(f'Gj.snitt Markert: {avg_marked:.2f}')

        # Legg til prosentandel som tekst under grafen
        axNok.text(
            0.5, 1.05,
            f'Gj.snitt er {prosent:.1f}% av Kronstad',
            transform=axNok.transAxes,
            ha='center',
            va='bottom'  # Bruk 'va' som 'top' hvis du vil at toppen av teksten skal være på y-posisjonen
        )



    # Håndter valgte stasjoner
    elif selected_station == 'Nordnes':
        avg_nordnes = np.mean(nord_nox)
        prosent = (avg_nordnes / avg_kronstad) * 100

        axNok.axhline(y=avg_nordnes, color='blue', linestyle='--')
        lines.append(axNok.lines[-1])
        labels.append(f'Gj.snitt Nordnes: {avg_nordnes:.2f}')

        axNok.text(
            0.5, 1.05,
            f'Gj.snitt er {prosent:.1f}% av Kronstad',
            transform=axNok.transAxes,
            ha='center',
            va='bottom'  # Bruk 'va' som 'top' hvis du vil at toppen av teksten skal være på y-posisjonen
        )

    elif selected_station == 'Kalfaret':
        avg_kalfaret = np.mean(kalfaret_nox)
        prosent = (avg_kalfaret / avg_kronstad) * 100

        axNok.axhline(y=avg_kalfaret, color='green', linestyle='--')
        lines.append(axNok.lines[-1])
        labels.append(f'Gj.snitt Kalfaret: {avg_kalfaret:.2f}')

        axNok.text(
            0.5, 1.05,
            f'Gj.snitt er {prosent:.1f}% av Kronstad',
            transform=axNok.transAxes,
            ha='center',
            va='bottom'  # Bruk 'va' som 'top' hvis du vil at toppen av teksten skal være på y-posisjonen
        )
    elif selected_station == 'Kronstad':
        avg_kronstad = np.mean(kron_nox)
        # Plott gjennomsnittslinjen for Kronstad
        axNok.axhline(y=avg_kronstad, color='red', linestyle='--')
        lines.append(axNok.lines[-1])
        labels.append(f'Gj.snitt Kronstad: {avg_kronstad:.2f}')

    axNok.set_title("NOX verdier")
    axNok.legend(lines, labels, loc='upper right')
    axNok.grid(linestyle='--')
    draw_label_and_ticks()

    # Plotter kartet
    axBergen.axis('off')
    img = mpimg.imread('Bergen.jpg')
    axBergen.imshow(img)
    axBergen.set_title("Kart Bergen")
    draw_circles_stations()
    plt.draw()



plot_graph()

# Koble slider til oppdateringsfunksjonen
def update(val):
    global days_interval, selected_station, marked_point
    days_interval = (int(slider.val[0]), int(slider.val[1]))
    selected_station = None
    marked_point = (0, 0)
    plot_graph()

slider.on_changed(update)

# Koble hendelseshåndtering
fig.canvas.mpl_connect('button_press_event', on_click)

# Vis plottet
plt.show()
