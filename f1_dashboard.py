# f1_dashboard.py
import os
import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

#cache
f1_cache = os.path.join(os.getcwd(), "f1_cache")

if not os.path.exists(f1_cache):
    os.makedirs(f1_cache, exist_ok=True)  # `exist_ok=True` prevents errors if it already exists

fastf1.Cache.enable_cache('f1_cache')

#Title
st.title("Formula 1 Race Analysis Dashboard")

# Sidebar for selecting race and year
year = st.sidebar.selectbox("Select Year", options=list(range(2022, 2026))[::-1])
gp = st.sidebar.selectbox("Select Grand Prix", options=["Melbourne", "Jeddah", "Bahrain", "Suzuka", "Shanghai", "Miami", "Imola", "Monaco", "Montreal",
"Barcelona", "Red Bull Ring", "Silverstone", "Hungaroring", "Spa-Francorchamps", "Zandvoort", "Monza",
"Marina Bay", "Austin", "Mexico City", "São Paulo", "Las Vegas", "Losail", "Yas Marina",
"Portimão", "Mugello", "Istanbul Park", "Nürburgring", "Sepang", "Hanoi"])

# Load session 
@st.cache_data(show_spinner=False)
def load_session(year, gp):
    session = fastf1.get_session(year, gp, 'R')
    # Disable loading of telemetry, weather, and messages to speed up load time
    session.load(telemetry=False, weather=False, messages=False)
    return session

try:
    with st.spinner("Loading session. This may take a moment..."):
        session = load_session(year, gp)

    st.success(f"{gp} Grand Prix - {year}")
except Exception as e:
    st.error(f"Error loading session: {e}")
    st.stop()

# Load lap data
laps = session.laps
laps = laps[laps['LapTime'].notnull()].copy()
laps['LapSeconds'] = laps['LapTime'].dt.total_seconds()
laps['TyreLife'] = laps.groupby(['Driver', 'Compound'], observed=True).cumcount() + 1
laps['DriverTeam'] = laps['Driver'] + " (" + laps['Team'] + ")"

# Speed Trap Visualization
st.header("Speed Trap Distribution")

driver_avg_speed = laps.groupby(['Driver', 'Team'])['SpeedST'].mean().reset_index()
driver_avg_speed = driver_avg_speed.sort_values(by='SpeedST', ascending=False)
driver_avg_speed['DriverTeam'] = driver_avg_speed['Driver'] + " (" + driver_avg_speed['Team'] + ")"
driver_order = driver_avg_speed['Driver'].tolist()
team_color_map = {team: px.colors.qualitative.Set3[i % 12] for i, team in enumerate(driver_avg_speed['Team'].unique())}

laps['Driver'] = pd.Categorical(laps['Driver'], categories=driver_order, ordered=True)
laps['TeamColor'] = laps['Team'].map(team_color_map)

fig1 = px.violin(
    laps,
    x='Driver',
    y='SpeedST',
    color='Team',
    box=True,
    points='all',
    category_orders={'Driver': driver_order},
    hover_data={'Team': True, 'Driver': True, 'SpeedST': True},
    labels={'SpeedST': 'Speed Trap (km/h)', 'Driver': 'Driver'},
)
fig1.update_layout(
    xaxis_title="Driver (Sorted by Avg Speed Trap)",
    yaxis_title="Speed Trap (km/h)",
    width=1100,
    height=600,
    violinmode='group'
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("""  
Each driver's distribution of Speed Trap readings is shown. The box represents the interquartile range and median, while points show all samples. 
Tighter boxes indicate consistent top-end speed, while spread-out data may suggest traffic or inconsistent DRS usage.

Speed traps don’t just expose the fastest cars—they reveal team philosophies! 
If a car tops the speed charts but struggles in lap times, it’s likely running a low-downforce, straight-line rocket setup, great for overtaking but tricky in corners. 
Meanwhile, a slower speed trap might mean the car is glued to the track with high downforce, making it a beast in the twisty sections but vulnerable on long straights. 
If you see a midfield team suddenly pop up near the top, it’s often a sign they’ve gone all-in on slipstreaming tactics during qualifying or have been experimenting with aggressive DRS usage. 
When a team nails the balance between blistering top speed and razor-sharp cornering, that’s when they graduate from contenders to champions!
""")

# Drag vs Downforce
st.header("Drag vs Downforce Tradeoff")

speed_trap = laps.groupby('Driver', observed=False)['SpeedST'].mean().reset_index()
avg_speed = laps.groupby('Driver', observed=False)['LapSeconds'].mean().reset_index()
race_positions = session.results[['Abbreviation', 'Position', 'Status']].rename(columns={'Abbreviation': 'Driver'})

merged_df = pd.merge(speed_trap, avg_speed, on='Driver')
merged_df = pd.merge(merged_df, race_positions, on='Driver', how='left')
merged_df['Race Position'] = merged_df.apply(lambda x: 'DNF' if x['Status'] != 'Finished' else str(int(x['Position'])), axis=1)
merged_df['Driver Label'] = merged_df['Race Position'] + " - " + merged_df['Driver']

fig2 = px.scatter(
    merged_df, 
    x='LapSeconds', 
    y='SpeedST', 
    text='Driver', 
    color='Driver Label',
    labels={'LapSeconds': 'Avg Lap Time (s)', 'SpeedST': 'Speed Trap (km/h)'},
    title='Drag vs Downforce Analysis'
)
fig2.update_traces(textposition='top center')
fig2.update_layout(showlegend=False)
st.plotly_chart(fig2, use_container_width=True)

st.markdown(""" 
Drivers in the top-left achieved high top speeds (low drag) but possibly at the cost of slower cornering.  
Those in bottom-right likely ran higher downforce setups, trading straight-line speed for lap consistency.

Think of it like picking between a jetpack and a parachute—one lets you fly down the straights, the other keeps you glued through the corners! 
Teams that lean too much into low drag might be lightning-fast in a straight line but struggle to keep the car stable through tricky chicanes. 
On the flip side, high downforce setups can make a car feel like it’s on rails, but they risk getting left behind on long straights. The real secret sauce? Finding that sweet spot where a car dances through corners without becoming a sitting duck on DRS zones. Some teams gamble on a ‘rocket ship’ setup for overtakes, while others play the long game with consistent lap times. 
The teams that master this tradeoff? They’re the ones fighting for podiums, not just participation trophies!
""")

# Tyre Degradation
st.header("Tyre Degradation Over Race Distance")

avg_lap_by_compound = laps.groupby(['LapNumber', 'Compound'], observed=True)['LapSeconds'].agg(['mean', 'std']).reset_index()
avg_lap_by_compound.rename(columns={'mean': 'AvgLapTime', 'std': 'StdLapTime'}, inplace=True)

fig3 = px.line(
    avg_lap_by_compound,
    x='LapNumber',
    y='AvgLapTime',
    color='Compound',
    error_y='StdLapTime',
    markers=True,
    labels={'LapNumber': 'Lap Number', 'AvgLapTime': 'Lap Time (s)'},
)
fig3.update_layout(width=1000, height=600, hovermode='x unified')
st.plotly_chart(fig3, use_container_width=True)


st.markdown(""" 
As laps progress, lap times generally increase – indicating tyre degradation.  
Soft compounds degrade faster, shown by sharper rises. Error bars show variability across all drivers using that compound.



Tyre degradation isn’t just about rubber wearing thin—it’s a delicate balancing act between speed, temperature, and grip. 
Think of it like a chef cooking the perfect steak: push too hard, and you’ll burn it (overheat the tyres); go too slow, and you’ll end up with an undercooked mess (loss of grip). 
Telemetry data shows that drivers with aggressive steering inputs tend to overheat their tyres faster, while those with smoother styles stretch tyre life like a seasoned Michelin-starred chef. 
Higher downforce cars get ‘cooked’ earlier due to increased friction, while low-downforce setups struggle with tyre ‘flavor loss’ later in the stint. 
The teams that master this culinary chaos? They end up serving podium finishes, while others are left chewing on regret!
""")


# Race Pace + Pit Strategy
st.header("Race Pace Evolution with Pit Stops")

finish_positions = laps.groupby('Driver', observed=True)['Position'].last()
top3_finishers = finish_positions[finish_positions.between(1, 3)].sort_values()
top3_laps = laps[laps['Driver'].isin(top3_finishers.index)].copy()
top3_laps['FinishPosition'] = top3_laps['Driver'].map(finish_positions)
top3_laps['PitStopText'] = np.where(top3_laps['PitInTime'].notnull(), 'Yes', 'No')

start_positions = laps.groupby('Driver', observed=True)['Position'].first()
top3_laps['StartPosition'] = top3_laps['Driver'].map(start_positions)
top3_laps['StartPosition'] = pd.to_numeric(top3_laps['StartPosition'], errors='coerce')
top3_laps['Position'] = pd.to_numeric(top3_laps['Position'], errors='coerce')
top3_laps['PositionChange'] = top3_laps['StartPosition'] - top3_laps['Position']
top3_laps['ChangeText'] = top3_laps['PositionChange'].apply(lambda x: f"+{x}" if x > 0 else (f"{x}" if x < 0 else "0"))

podium_styles = {1: dict(color='gold', symbol='circle'),
                2: dict(color='silver', symbol='square'),
                3: dict(color='peru', symbol='diamond')}

fig4 = go.Figure()

for driver in top3_finishers.index:
    d_laps = top3_laps[top3_laps['Driver'] == driver]
    pos = int(d_laps['FinishPosition'].iloc[0])
    style = podium_styles.get(pos, dict(color='blue', symbol='circle'))

    fig4.add_trace(go.Scatter(
        x=d_laps['LapNumber'],
        y=d_laps['LapSeconds'],
        mode='lines+markers',
        name=f"{driver} (P{pos})",
        marker=dict(color=style['color'], symbol=style['symbol']),
        line=dict(color=style['color']),
        customdata=np.stack([
            d_laps['Driver'],
            d_laps['Team'],
            d_laps['Compound'],
            d_laps['Position'],
            d_laps['ChangeText'],
            d_laps['PitStopText']
        ], axis=-1),
        hovertemplate=(
            "Driver: %{customdata[0]}<br>"
            "Team: %{customdata[1]}<br>"
            "Lap: %{x}<br>"
            "Lap Time: %{y:.2f}s<br>"
            "Tyre: %{customdata[2]}<br>"
            "Race Pos: %{customdata[3]}<br>"
            "Change: %{customdata[4]}<br>"
            "Pit Stop: %{customdata[5]}"
        )
    ))

# Pit stop markers
pit_stops = top3_laps[top3_laps['PitInTime'].notnull()]
fig4.add_trace(go.Scatter(
    x=pit_stops['LapNumber'],
    y=pit_stops['LapSeconds'],
    mode='markers',
    name='Pit Stop',
    marker=dict(symbol='x', size=12, color='red'),
    customdata=pit_stops[['Driver']],
    hovertemplate="Pit Stop<br>Driver: %{customdata[0]}<br>Lap: %{x}<br>Lap Time: %{y:.2f}s"
))

fig4.update_layout(
    title='Top 3 Drivers - How did they secure the podium finish?',
    xaxis_title='Lap Number',
    yaxis_title='Lap Time (s)',
    width=1100,
    height=600,
    hovermode='closest'
)

st.plotly_chart(fig4, use_container_width=True)

fastest_lap = laps.loc[laps['LapSeconds'].idxmin()]
fastest_driver = fastest_lap['Driver']
fastest_lap_number = fastest_lap['LapNumber']
fastest_lap_time = fastest_lap['LapSeconds']

st.markdown(f"**Fastest Lap:** {fastest_driver} on Lap {fastest_lap_number} with a time of {fastest_lap_time:.3f} seconds.")

st.markdown(""" 
This graph shows how lap times evolved for the top 3 drivers. Sharp spikes typically denote out-laps or in-laps. Pit stops are shown as red X marks. Changes in line trends often reflect strategy calls like undercuts or tyre switches.

The battle for race pace isn’t just about speed—it’s about knowing when to push and when to hold back. 
A sudden dip in lap times before a pit stop can indicate a driver squeezing out every ounce of grip before a fresh set of tyres. Conversely, a gradual decline might signal careful tyre management, possibly due to a high tyre-wear setup. 
If a driver gains positions post-pit stop, they’ve executed an ‘undercut’—pitting earlier to take advantage of fresh rubber while rivals struggle on worn tyres. This graph also exposes teams’ pit stop efficiency—longer pit stops can cost crucial seconds, making even the fastest drivers vulnerable to a well-timed strategy move. 
A quick look at throttle traces from telemetry can reveal who is managing acceleration phases better, often the key to extracting consistent performance.

That's why, when you see a driver suddenly shaving off tenths towards the end? that’s not luck, that’s strategy unfolding like a thriller novel—gripping, calculated, and perfectly timed for a dramatic finish!
""") 
