# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import time
import helics as h
import logging
import pandas as pd
import numpy as np
import argparse

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def destroy_federate(fed):
    grantedtime = h.helicsFederateRequestTime(fed, h.HELICS_TIME_MAXTIME)
    h.helicsFederateDisconnect(fed)
    h.helicsFederateDestroy(fed)
    logger.info("Federate finalized")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', nargs=1)
    args = parser.parse_args()

    fed = h.helicsCreateCombinationFederateFromConfig("1c_Control_2.json")
    federate_name = h.helicsFederateGetName(fed)
    logger.info("HELICS Version: {}".format(h.helicsGetVersion()))
    logger.info("{}: Federate {} has been registered".format(federate_name, federate_name))

    endpoint_count = h.helicsFederateGetEndpointCount(fed)
    subkeys_count = h.helicsFederateGetInputCount(fed)
    endid = {}
    subid = {}
    ev_names = []

    for i in range(endpoint_count):
        ep = h.helicsFederateGetEndpointByIndex(fed, i)
        endid[f"m{i}"] = ep
        name = h.helicsEndpointGetName(ep).split("/")[-1]
        ev_names.append(name)
        logger.info(f"{federate_name}: Registered Endpoint ---> {name}")

    for i in range(subkeys_count):
        subid[f"m{i}"] = h.helicsFederateGetInputByIndex(fed, i)
        h.helicsInputSetDefaultComplex(subid[f"m{i}"], 0, 0)
        logger.info(f"{federate_name}: Registered Subscription ---> {h.helicsInputGetTarget(subid[f'm{i}'])}")

    h.helicsFederateEnterExecutingMode(fed)

    plotting = True
    hours = 24
    #total_interval = int(60 * 60 * hours)
    total_interval = 1
    grantedtime = -1
    update_interval = 20 * 60
    feeder_limit_upper = 4.2e6
    feeder_limit_lower = 2.6e6
    EV_data = {name: [] for name in ev_names}
    time_sim = []
    feeder_real_power = []

    if plotting:
        ax = {}
        fig = plt.figure()
        fig.subplots_adjust(hspace=0.4, wspace=0.4)
        ax['Feeder_2'] = plt.subplot(313)
        for i, name in enumerate(ev_names):
            ax[name] = plt.subplot(331 + i)

    for t in range(0, total_interval, update_interval):
        while grantedtime < t:
            grantedtime = h.helicsFederateRequestTime(fed, t)

        time_sim.append(t / 3600)

        rload_total = 0
        iload_total = 0
        for i in range(subkeys_count):
            demand = h.helicsInputGetComplex(subid[f"m{i}"])
            rload_total += demand.real
            iload_total += demand.imag
        feeder_real_power.append(rload_total)

        # Initialize all EV values as NaN in case no message is received this step
        current_ev_values = {name: np.nan for name in ev_names}

        for i in range(endpoint_count):
            ep = endid[f"m{i}"]
            name = ev_names[i]
            latest_val = None

            while h.helicsEndpointHasMessage(ep):
                msg = h.helicsEndpointGetMessage(ep)
                try:
                    latest_val = complex(h.helicsMessageGetString(msg)).real / 1000
                except Exception as e:
                    logger.warning(f"Could not parse message for {name}: {e}")
                    continue

            if latest_val is not None:
                current_ev_values[name] = latest_val

        # Store the values
        for name in ev_names:
            EV_data[name].append(current_ev_values[name])

        logger.info(f"{federate_name}: Granted Time = {grantedtime}")
        logger.info(f"{federate_name}: Load = {rload_total/1e3:.2f} kW + {iload_total/1e3:.2f} kVAr")

        if feeder_real_power[-1] > feeder_limit_upper:
            for idx in range(endpoint_count):
                h.helicsEndpointSendBytes(endid[f"m{idx}"], '0.0+0.0j')
            logger.info(f"{federate_name}: Overload action executed")
        elif feeder_limit_lower < feeder_real_power[-1] < feeder_limit_upper:
            for idx in range(2):
                h.helicsEndpointSendBytes(endid[f"m{idx}"], '210000+0.0j')
            logger.info(f"{federate_name}: Safe range action executed")
        else:
            for idx in range(endpoint_count):
                h.helicsEndpointSendBytes(endid[f"m{idx}"], '200000+0.0j')
            logger.info(f"{federate_name}: Low-load action executed")

        if plotting:
            ax['Feeder_2'].clear()
            ax['Feeder_2'].plot(time_sim, np.array(feeder_real_power)/1e6)
            ax['Feeder_2'].set_ylabel("Feeder Load (MW)")
            ax['Feeder_2'].set_xlabel("Time (Hours)")
            ax['Feeder_2'].grid()

            for name in ev_names:
                ax[name].clear()
                ax[name].plot(time_sim, EV_data[name])
                ax[name].set_title(name)
                ax[name].set_ylabel("EV Output (kW)")
                ax[name].set_xlabel("Time (Hours)")
                ax[name].grid()

            plt.show(block=False)
            plt.pause(0.01)

    if plotting:
        df = pd.DataFrame(EV_data)
        df["time"] = time_sim
        df["feeder_load_W"] = feeder_real_power
        df.to_csv("1c_EV_Outputs_2.csv", index=False)

    logger.info(f"{federate_name}: Finished time loop, finalizing federate.")
    destroy_federate(fed)
