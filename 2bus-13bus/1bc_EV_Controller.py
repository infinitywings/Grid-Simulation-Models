# -*- coding: utf-8 -*-
"""
EV Controller for 2bus-13bus Co-Sim
Updated to:
- Turn OFF all EV stations when feeder load >= upper limit
- EV1 & EV2 ON in safe range, others OFF
- All EVs ON when feeder load is low
"""
import matplotlib.pyplot as plt
import helics as h
import logging
import pandas as pd
import numpy as np
import argparse
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def destroy_federate(fed):
    """Cleanly finalize the HELICS federate."""
    h.helicsFederateRequestTime(fed, h.HELICS_TIME_MAXTIME)
    h.helicsFederateDisconnect(fed)
    h.helicsFederateDestroy(fed)
    logger.info("Federate finalized")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', nargs=1)
    args = parser.parse_args()

    # ---------------------------------------------------------------------
    # Register federate from JSON
    # ---------------------------------------------------------------------
    fed = h.helicsCreateCombinationFederateFromConfig("1c_Control.json")
    federate_name = h.helicsFederateGetName(fed)
    logger.info("HELICS Version: {}".format(h.helicsGetVersion()))
    logger.info("{}: Federate {} has been registered".format(federate_name, federate_name))

    endpoint_count = h.helicsFederateGetEndpointCount(fed)
    subkeys_count = h.helicsFederateGetInputCount(fed)

    # ---------------------------------------------------------------------
    # Endpoints and subscriptions
    # ---------------------------------------------------------------------
    endid = {}
    subid = {}
    ev_names = []

    # Endpoints (EV chargers)
    for i in range(endpoint_count):
        ep = h.helicsFederateGetEndpointByIndex(fed, i)
        endid[f"m{i}"] = ep
        end_name = h.helicsEndpointGetName(ep)
        ev_name = end_name.split('/')[-1]
        ev_names.append(ev_name)
        logger.info("{}: Registered Endpoint ---> {}".format(federate_name, end_name))

    # Subscriptions (feeder load from GridLAB-D)
    for i in range(subkeys_count):
        sub = h.helicsFederateGetInputByIndex(fed, i)
        subid[f"m{i}"] = sub
        h.helicsInputSetDefaultComplex(sub, 0, 0)
        sub_key = h.helicsInputGetTarget(sub)
        logger.info("{}: Registered Subscription ---> {}".format(federate_name, sub_key))

    # ---------------------------------------------------------------------
    # Enter execution mode
    # ---------------------------------------------------------------------
    h.helicsFederateEnterExecutingMode(fed)

    plotting = True      # Enable plotting at the end
    hours = 24
    total_interval = int(60 * 60 * hours)
    grantedtime = -1

    # Configurable EV control interval (seconds); default 60s for experiments
    CONTROLLER_INTERVAL_SEC = int(os.getenv("CONTROLLER_INTERVAL_SEC", "60"))
    update_interval = CONTROLLER_INTERVAL_SEC

    # Feeder limits (W)
    feeder_limit_upper = 4.8e6
    feeder_limit_lower = 2.6e6

    # Data storage
    EV_data = {name: [] for name in ev_names}
    time_sim = []
    feeder_real_power = []

    # ---------------------------------------------------------------------
    # Main time loop
    # ---------------------------------------------------------------------
    for t in range(0, total_interval, update_interval):

        # Synchronize HELICS time
        while grantedtime < t:
            grantedtime = h.helicsFederateRequestTime(fed, t)

        # Time in hours
        time_sim.append(t / 3600.0)

        # ---------------------- Read feeder load -------------------------
        rload_total = 0.0
        iload_total = 0.0
        for i in range(subkeys_count):
            sub = subid[f"m{i}"]
            demand = h.helicsInputGetComplex(sub)
            rload_total += demand.real
            iload_total += demand.imag

        feeder_real_power.append(rload_total)

        # ---------------------- Read EV messages -------------------------
        # Initialize EV values with NaN for this time step
        current_ev_values = {name: np.nan for name in ev_names}

        for i in range(endpoint_count):
            end_point = endid[f"m{i}"]
            ev_name = ev_names[i]

            latest_val = None
            end_point_msg_obj = None

            # Clear pending messages, keep only the most recent one
            while h.helicsEndpointHasMessage(end_point):
                end_point_msg_obj = h.helicsEndpointGetMessage(end_point)

            if end_point_msg_obj is not None:
                try:
                    EV_now = complex(h.helicsMessageGetString(end_point_msg_obj))
                    latest_val = EV_now.real / 1000.0  # W -> kW
                except Exception as e:
                    logger.warning(
                        f"{federate_name}: Could not parse EV message at endpoint {ev_name}: {e}"
                    )

            if latest_val is not None:
                current_ev_values[ev_name] = latest_val

        # Store EV values (one per EV per time step)
        for name in ev_names:
            EV_data[name].append(current_ev_values[name])

        logger.info(
            "{}: Federate Granted Time = {}".format(federate_name, grantedtime)
        )
        logger.info(
            "{}: Total Feeder Load is {} kW + {} kVARj ".format(
                federate_name,
                round(rload_total / 1000.0, 2),
                round(iload_total / 1000.0, 2),
            )
        )

        # -----------------------------------------------------------------
        # CONTROL LOGIC
        # -----------------------------------------------------------------
        P = feeder_real_power[-1]
        action_taken = "unknown"

        # Case 1: Overload condition → turn OFF all EV stations
        if P >= feeder_limit_upper:
            logger.info(
                "{}: OVERLOAD: P = {:.2f} MW >= {:.2f} MW, turning OFF all EV stations.".format(
                    federate_name, P / 1e6, feeder_limit_upper / 1e6
                )
            )

            # Turn OFF all EVs (all endpoints)
            for i in range(endpoint_count):
                h.helicsEndpointSendBytes(endid[f"m{i}"], '0.0+0.0j')

            logger.info("{}: All EVs are now OFF due to overload.".format(federate_name))
            action_taken = "overload_off"

        # Case 2: Safe range → only EV1 and EV2 ON, others OFF
        elif feeder_limit_lower < P < feeder_limit_upper:
            logger.info(
                "{}: SAFE RANGE: P = {:.2f} MW, EV1 & EV2 ON, others OFF.".format(
                    federate_name, P / 1e6
                )
            )

            # Turn ON EV1 and EV2
            h.helicsEndpointSendBytes(endid["m0"], '210000+0.0j')  # EV1
            h.helicsEndpointSendBytes(endid["m1"], '200000+0.0j')  # EV2
            h.helicsEndpointSendBytes(endid["m2"], '210000+0.0j')  # EV1
            h.helicsEndpointSendBytes(endid["m3"], '200000+0.0j')  # EV2
            h.helicsEndpointSendBytes(endid["m4"], '210000+0.0j')  # EV1
            h.helicsEndpointSendBytes(endid["m5"], '200000+0.0j')  # EV2
            action_taken = "safe_range_ev1_ev2_only"

            # Turn OFF EV3–EV6 (if they exist)
            # for i in range(2, endpoint_count):
            #     h.helicsEndpointSendBytes(endid[f"m{i}"], '0.0+0.0j')
            #
            # logger.info("{}: EV3, EV4, EV5, and EV6 are OFF.".format(federate_name))

        # Case 3: Below or equal to lower limit → all EVs ON
        else:  # P <= feeder_limit_lower
            logger.info(
                "{}: LOW LOAD: P = {:.2f} MW <= {:.2f} MW, turning ON ALL EVs.".format(
                    federate_name, P / 1e6, feeder_limit_lower / 1e6
                )
            )

            # Turn ON all EVs (same pattern as before)
            powers = ['210000+0.0j', '200000+0.0j', '200000+0.0j',
                      '200000+0.0j', '200000+0.0j', '206000+0.0j']
            for i in range(endpoint_count):
                p_cmd = powers[i] if i < len(powers) else '200000+0.0j'
                h.helicsEndpointSendBytes(endid[f"m{i}"], p_cmd)

            logger.info("{}: All EVs are now charging.".format(federate_name))
            action_taken = "low_load_all_on"

        logger.info(
            f"[CONTROLLER_ACTION] sim_time={grantedtime}s load_kw={P/1000.0:.1f} "
            f"interval={update_interval}s action={action_taken}"
        )

    # ---------------------------------------------------------------------
    # Plotting and saving results (after loop)
    # ---------------------------------------------------------------------
    if plotting:
        # Save data first
        EV_data["time"] = time_sim
        EV_data["feeder_load"] = feeder_real_power
        pd.DataFrame.from_dict(EV_data).to_csv("1c_EV_Outputs.csv", header=True, index=False)

        # EV names for plotting
        plot_ev_names = [k for k in EV_data if k not in ["time", "feeder_load"]]
        n_evs = len(plot_ev_names)

        # Sanity check lengths
        logger.info(f"len(time_sim) = {len(time_sim)}")
        logger.info(f"len(feeder_real_power) = {len(feeder_real_power)}")
        for name in plot_ev_names:
            logger.info(f"len(EV_data['{name}']) = {len(EV_data[name])}")

        # Create figure with Feeder Load + EVs
        plt.figure(figsize=(10, 3 * (n_evs + 1)))

        # Feeder subplot
        plt.subplot(n_evs + 1, 1, 1)
        plt.plot(time_sim, feeder_real_power, label="Feeder Load", color='black')
        plt.plot(np.linspace(0, 24, 25), feeder_limit_upper * np.ones(25), 'r--', label="Upper Limit")
        plt.plot(np.linspace(0, 24, 25), feeder_limit_lower * np.ones(25), 'g--', label="Lower Limit")
        plt.xlabel("Time (Hrs)")
        plt.ylabel("Feeder Load (W)")
        plt.title("Feeder Load Over Time")
        plt.grid()
        plt.legend()

        # EV subplots
        for i, ev_name in enumerate(plot_ev_names):
            plt.subplot(n_evs + 1, 1, i + 2)
            plt.plot(time_sim, EV_data[ev_name], color='black', label=ev_name)
            plt.xlabel("Time (Hrs)")
            plt.ylabel("EV Output (kW)")
            plt.title(ev_name.replace('EV', 'EV Charger '))
            plt.grid(True)
            plt.xlim([0, 24])

        plt.tight_layout()
        plt.savefig("./output/1c_Feeder_and_EVs_subplot.png", dpi=300)

    # ---------------------------------------------------------------------
    # Finalize federate
    # ---------------------------------------------------------------------
    t_final = 60 * 60 * 24
    while grantedtime < t_final:
        grantedtime = h.helicsFederateRequestTime(fed, t_final)

    logger.info("{}: Destroying federate".format(federate_name))
    destroy_federate(fed)
