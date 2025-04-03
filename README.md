# F1 Race Analysis Dashboard
This dashboard visualizes Formula 1 race data using FastF1. Explore speed trap metrics, tyre degradation, drag-downforce tradeoffs, and race strategy insights for any selected Grand Prix from 2022 onwards.

## Features

### 1. Speed Trap Distribution
<img src="img/image_2025-04-04_02-27-54.png" width="500">

- Violin plot of speed trap readings for each driver
- Sorted by average performance
- Colored by team
- Insightful interpretation of team setup philosophy

### 2. Drag vs Downforce Tradeoff
<img src="img/image_2025-04-04_02-29-02.png" width="500">

- Scatter plot of average lap time vs top speed
- Shows setup tradeoffs (low drag vs high downforce)
- Driver finishing position indicated in the legend

### 3. Tyre Degradation
<img src="img/image_2025-04-04_02-32-51.png" width="500">

- Compound-wise average lap time over race distance
- Error bars indicate variability
- Shows how different tyre compounds age during a race

### 4. Race Pace & Strategy (Top 3 drivers)
<img src="img/image_2025-04-04_02-33-18.png" width="500">

- Lap-by-lap graph of top 3 finishers
- Pit stop markers
- Driver position changes from start to finish
- Highlights undercut strategies and consistency


## Demo

[Launch Dashboard on Cloud](#) – (Insert link after deployment)

---

## Install dependencies:
```bash
pip install -r requirements.txt
```
## Run the App
```bash
streamlit run f1_dashboard.py
```
## License
MIT License

## Author
Made with fuel and finesse by **Siddharth** 


