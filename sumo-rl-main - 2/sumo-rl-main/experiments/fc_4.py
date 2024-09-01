import os
import subprocess
import traci
import matplotlib.pyplot as plt  # Import the matplotlib library

# Paths to SUMO tools
sumo_bin = ""nets\4x4-Lucas\4x4.sumocfg""  # Replace with the path to your SUMO executable
sumo_cmd = [sumo_bin, "-c", "my_simulation.sumocfg"]

# Create the SUMO configuration file
with open("my_simulation.sumocfg", "w") as cfg_file:
    cfg_file.write('<configuration>\n')
    cfg_file.write('    <time>\n')
    cfg_file.write('        <begin value="0"/>\n')
    cfg_file.write('        <end value="10000"/>\n')  # Set the end time to 10000 seconds
    cfg_file.write('    </time>\n')
    cfg_file.write('    <input>\n')
    cfg_file.write('        <net-file value="my_network.net.xml"/>\n')
    cfg_file.write('        <route-files value="my_routes.rou.xml"/>\n')
    cfg_file.write('    </input>\n')
    cfg_file.write('</configuration>\n')

# Run the SUMO simulation
subprocess.Popen(sumo_cmd)

# Connect to the simulation using TraCI
traci.start(sumo_cmd)

# Initialize variables for calculating moving average
window_size = 60  # Number of seconds for the moving average window
waiting_times = []
moving_averages = []
time_steps = []

# Simulation loop
time_step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    time_step += 1
    
    # Calculate waiting time for each vehicle
    for veh_id in traci.vehicle.getIDList():
        waiting_time = traci.vehicle.getAccumulatedWaitingTime(veh_id)
        waiting_times.append(waiting_time)
    
    # Keep the moving average window size
    if time_step >= window_size:
        moving_average = sum(waiting_times[-window_size:]) / window_size
        moving_averages.append(moving_average)
        time_steps.append(time_step)
    
# Clean up TraCI connection
traci.close()

# Plot the moving average waiting time
plt.plot(time_steps, moving_averages)
plt.xlabel("Time (seconds)")
plt.ylabel("Moving Average Waiting Time")
plt.title("Moving Average Waiting Time of Vehicles")
plt.grid(True)
plt.show()

