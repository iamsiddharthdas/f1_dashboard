# F1 Race Analysis Dashboard
(screenshots)
This dashboard visualizes Formula 1 race data using FastF1. Explore speed trap metrics, tyre degradation, drag-downforce tradeoffs, and race strategy insights for any selected Grand Prix from 2022 onwards.

## Features

### 1. Speed Trap Distribution
- Violin plot of speed trap readings for each driver
- Sorted by average performance
- Colored by team
- Insightful interpretation of team setup philosophy

### 2. Drag vs Downforce Tradeoff
- Scatter plot of average lap time vs top speed
- Shows setup tradeoffs (low drag vs high downforce)
- Driver finishing position indicated in the legend

### 3. Tyre Degradation
- Compound-wise average lap time over race distance
- Error bars indicate variability
- Shows how different tyre compounds age during a race

### 4. Race Pace & Strategy
- Lap-by-lap graph of top 3 finishers
- Pit stop markers
- Driver position changes from start to finish
- Highlights undercut strategies and consistency

---

## Demo

[Launch Dashboard on Cloud](#) – (Insert link after deployment)

## Requirements

1. Install dependencies:

```bash
pip install -r requirements.txt


2. Run the App

streamlit run f1_dashboard.py

How to Run Locally (Clone the Repo)

```bash
git clone https://github.com/your-username/f1-dashboard.git
cd f1-dashboard


## License

MIT License

## Author

Made with fuel and finesse by Siddharth




