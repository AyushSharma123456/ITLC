#!/usr/bin/env python
# coding: utf-8

# In[2]:


from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import time
import optparse
import random
import serial
import numpy as np
import torch
import torch.optim as optim
import torch.nn.functional as F
import torch.nn as nn
import matplotlib.pyplot as plt
import pandas as pd


# In[3]:


# we need to import python modules from the $SUMO_HOME/tools directory
if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


# In[ ]:


total_time_list=[]

def get_waiting_times():
    for e in range(1,2):
        print("Epoch",e)
        traci.start(["sumo", "-c", "configuration.sumocfg"])

        step = 0
        max_steps = 10000
        total_avg_time_list=[]
        total_emissions_stopped_list=[]
        teleported_vehicles_list=[]
        delayed_vehicles_list=[]
        total_avg_time=0
        total_emissions_stopped=0
        total_teleported_vehicles=0


        while step < max_steps:
            traci.simulationStep()
            vehicles = traci.vehicle.getIDList()
            teleported_vehicles = traci.vehicle.getTeleportingIDList()
            total_teleported_vehicles+=len(teleported_vehicles)
            speeds = [traci.vehicle.getSpeed(vehicle) for vehicle in vehicles]
            waiting_times = [traci.vehicle.getWaitingTime(vehicle) for vehicle in vehicles]
            emission_info=[traci.vehicle.getCO2Emission(vehicle) for vehicle in vehicles]
            stopped_vehicles = [vehicle for vehicle, speed in zip(vehicles, speeds) if speed < 0.1]
            emissions_stopped = [traci.vehicle.getCO2Emission(vehicle) for vehicle in stopped_vehicles]
            system_total_waiting_time= sum(waiting_times)
            system_mean_waiting_time= 0.0 if len(vehicles) == 0 else np.mean(waiting_times)
            system_total_emissions= sum(emission_info)
            system_total_emissions_stopped= sum(emissions_stopped)
            system_mean_emissions= 0.0 if len(vehicles) == 0 else np.mean(emission_info)
            system_mean_emissions_stopped= 0.0 if len(stopped_vehicles) == 0 else np.mean(emissions_stopped)
            total_emissions_stopped += system_total_emissions_stopped
            total_avg_time_list.append(system_mean_waiting_time)
            teleported_vehicles_list.append(len(teleported_vehicles))
            total_emissions_stopped_list.append(system_total_emissions_stopped)
            vehicles_with_delay_more_than_2_minutes = 0

            for vehicle in vehicles:
                departure_delay = traci.vehicle.getDepartDelay(vehicle)
                if departure_delay > 120:  # 600 seconds = 10 minutes
                    vehicles_with_delay_more_than_2_minutes += 1

            delayed_vehicles_list.append(vehicles_with_delay_more_than_2_minutes)

            step += 1
            
        print("total_emissions_stopped",total_emissions_stopped)
        print("Avg_waiting_time",sum(total_avg_time_list)/len(total_avg_time_list))
        print("vehicles_with_delay_more_than_2_minutes", vehicles_with_delay_more_than_2_minutes)
        print("total_teleported_vehicles", total_teleported_vehicles)
        # Create a DataFrame from the collected data
        data = pd.DataFrame({
        'Total Emissions Stopped': total_emissions_stopped_list,
        'Average Waiting Time': total_avg_time_list,
        'Vehicles with Delay More Than 2 Minutes': delayed_vehicles_list,
        "total_teleported_vehicles": teleported_vehicles_list,
        })

        # Specify the Excel file name
        excel_file = 'traffic_data_teleported_trans_vt.xlsx'

        # Save the DataFrame to an Excel file
        data.to_excel(excel_file, index=False)

        print(f'Data saved to {excel_file}')

        traci.close()

if __name__ == "__main__":
    get_waiting_times()


