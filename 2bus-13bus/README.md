# T&D Co-Simulation Testbed

## Overview

The T&D co-simulation testbed integrates transmission and distribution systems with EV charging infrastructure and a controller for peak-demand management. The setup consists of:

1. **Transmission System**

   * One IEEE 9-bus transmission system modeled in **GridPACK** (`gpk-left-fed.cpp` and related files).
   * The transmission grid is connected to two GridLAB-D models (distribution systems) at Bus 2 and Bus 3, which correspond to Node 650 in each distribution system.

2. **Distribution Systems**

   * Two IEEE 123-node distribution systems modeled in **GridLAB-D**:

     * `1c_IEEE_123_feeder.glm`
     * `1c_IEEE_123_feeder_2.glm`
     
   * Six EV charging stations (CSs) integrated into each distribution system at the following buses:

     ```
     EV_bus_numbers = [5, 2, 88, 92, 107, 114]
     ```

3. **Controller**

   * One Python-based EV controller (`1bc_EV_Controller.py`) manages the charging stations in `1c_IEEE_123_feeder.glm`.
   * The controller performs **demand shaving during peak hours**.

---

## Steps to Run the Testbed

1. **Compile the GridPACK model**

   ```bash
   mkdir build && cd build
   cmake ..
   make
   ```

2. **Run the co-simulation**

   ```bash
   helics run --path=gpk-gld-cosim.json
   ```

---

## Potential Attack Surfaces

1. EV charging stations.
2. Switches connecting EV CSs to distribution nodes.
3. Switches connecting two EV CSs to battery energy storage in the `1c_IEEE_123_feeder.glm` model.
4. The EV CS controller directly.

---

## Additional Notes

This co-simulation testbed considers 1 transmission system and 2 distribution systems where we want to control the EVs of one of the distribution systems.

Key details:
- Originally intended to use a 300-bus transmission system, but scaled down to a 9-bus system for computational feasibility
- The 9-bus transmission system connects to 2 IEEE 123-node distribution systems
- One of the distribution systems (glm1) includes 6 EV stations where EV1 is attached to a battery energy storage system that connects during peak demand as an islanded system
- Uses California traffic patterns for 3 EV stations (EV1, EV5, and EV6)

## Important Info about the Potential Spots for Attackers:

<details>
<summary>************************** EV CS 6 ************************</summary>

EV: EV6  
Switch: swEV6  
Switch phases: AN  
From (link): l114  
To (node/load): EV6  
Switch status: CLOSED  
Load phases: AN  
Nominal voltage (V): 2401.7771  
Power prop: constant_power_A  
Power source: player  
Player ref: ev6_player.value  
Max power (VA): 200 KW  
Recorder properties: constant_power_A  
Recorder interval (s): 60  
Recorder file: output/1c_IEEE_123_feeder_0_EV6.csv  
Recorder window start: 2013-08-28 00:00:00  
Recorder window end: 2013-08-29 00:00:00  
Upstream/Context: From l114  
Abnormal P target (VA): 2-4 MW

</details>

---

<details>
<summary>************************** EV CS 5 ************************</summary>

EV: EV5  
Switch: swEV5  
Switch phases: BN  
From (link): l107  
To (node/load): EV5  
Switch status: CLOSED  
Load phases: BN  
Nominal voltage (V): 2401.7771  
Power prop: constant_power_B  
Power source: player  
Player ref: ev5_player.value  
Max power (VA): 200 KW  
Recorder properties: constant_power_B  
Recorder interval (s): 60  
Recorder file: output/1c_IEEE_123_feeder_0_EV5.csv  
Recorder window start: 2013-08-28 00:00:00  
Recorder window end: 2013-08-29 00:00:00  
Upstream/Context: From l107  
Abnormal P target (VA): 2-4 MW

</details>

---

<details>
<summary>************************** EV CS 4 ************************</summary>

EV: EV4  
Switch: swEV4  
Switch phases: CN  
From (link): l92  
To (node/load): EV4  
Switch status: CLOSED  
Load phases: CN  
Nominal voltage (V): 2401.7771  
Power prop: constant_power_C  
Power source: player  
Player ref: ev4_player.value  
Max power: 200 KW  
Recorder properties: constant_power_C  
Recorder interval (s): 60  
Recorder file: output/1c_IEEE_123_feeder_0_EV4.csv  
Recorder window start: 2013-08-28 00:00:00  
Recorder window end: 2013-08-29 00:00:00  
Upstream/Context: From l92  
Abnormal P target (VA): 2-4 MW

</details>

---

<details>
<summary>************************** EV CS 3 ************************</summary>

EV: EV3  
Switch: swEV3  
Switch phases: AN  
From (link): l88  
To (node/load): EV3  
Switch status: CLOSED  
Load phases: AN  
Nominal voltage (V): 2401.7771  
Power prop: constant_power_A  
Power source: player  
Player ref: ev3_player.value  
Max power: 200 KW  
Recorder properties: constant_power_A  
Recorder interval (s): 60  
Recorder file: output/1c_IEEE_123_feeder_0_EV3.csv  
Recorder window start: 2013-08-28 00:00:00  
Recorder window end: 2013-08-29 00:00:00  
Upstream/Context: From l88  
Abnormal P target (VA): 2-4 MW

</details>

---

<details>
<summary>************************** EV CS 2 ************************</summary>

EV: EV2  
Switch: swEV2  
Switch phases: BN  
From (link): l2  
To (node/load): EV2  
Switch status: CLOSED  
Load phases: BN  
Nominal voltage (V): 2401.7771  
Power prop: constant_power_B  
Power source: fixed  
Player ref: —  
Base power : 200 KW  
Recorder properties: constant_power_B  
Recorder interval (s): 60  
Recorder file: output/1c_IEEE_123_feeder_0_EV2.csv  
Recorder window start: 2013-08-28 00:00:00  
Recorder window end: 2013-08-29 00:00:00  
Upstream/Context: From l2  
Abnormal P target (VA): 2-4 MW

</details>

---

<details>
<summary>************************** EV CS 1 ************************</summary>

EV: EV1  
Switch: swEV1  
Switch phases: CN  
From (link): l5  
To (node/load): EV1  
Switch status: CLOSED  
Load phases: CN  
Nominal voltage (V): 2401.7771  
Power prop: constant_power_C  
Power source: fixed  
Player ref: —  
Base power : 200 KW  
Recorder properties: constant_power_C  
Recorder interval (s): 60  
Recorder file: output/1c_IEEE_123_feeder_0_EV1.csv  
Recorder window start: 2013-08-28 00:00:00  
Recorder window end: 2013-08-29 00:00:00  
Upstream/Context: From l5  
Abnormal P target (VA): 2-4 MW

</details>
