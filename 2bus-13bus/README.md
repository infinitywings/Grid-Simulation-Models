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

## Simulation model and EV controller details

### Simulation model (2bus-13bus)
- **Transmission**: GridPACK-based IEEE 9-bus system (`gpk-left-fed.cpp`, `pf_app.cpp`) feeds two GridLAB-D feeders at Bus 2 and Bus 3 (mapped to Node 650 in each feeder) via HELICS (`gpk-gld-cosim.json`).
- **Distribution**: Two IEEE 123-node feeders:
  - `1c_IEEE_123_feeder.glm`: includes six controllable EV charging stations at buses 5, 2, 88, 92, 107, and 114. EV1 is paired with a battery storage switch that can island during peak conditions.
  - `1c_IEEE_123_feeder_2.glm`: parallel uncontrolled feeder.
- **HELICS exchange (key topics)**:
  - GridLAB-D publishes feeder power `gld_hlc_conn/Sa,Sb,Sc` and subscribes to transmission voltages `gridpack/Va,Vb,Vc`.
  - GridPACK publishes `gridpack/Va,Vb,Vc` and subscribes to feeder power `gld_hlc_conn/Sa,Sb,Sc`.
  - EV controller publishes setpoints `EV_Controller/EV1-6 → gld_hlc_conn/EV1-6` and (for storage-capable buses) switch commands; it subscribes to `gld_hlc_conn/Sa,Sb,Sc` for feeder loading.
- **Operating limits (controller-driven)**: feeder load lower limit 2.6 MW; upper limit 4.8 MW in the primary controller (4.2 MW in the demo/secondary controller). Nominal line-to-neutral voltage ≈ 2401.8 V.

### EV controllers

**Primary controller (`1bc_EV_Controller.py`, config `1c_Control.json`)**
- Registers HELICS combination federate from JSON, discovers EV endpoints dynamically, and subscribes to feeder real/reactive power.
- Runs a 24-hour loop with a configurable interval (`CONTROLLER_INTERVAL_SEC`, default 60 s).
- Control logic (acts on real power `P` from `gld_hlc_conn/S*`):
  - `P ≥ 4.8 MW`: send a zero-power command (`0+0j`, complex zero) to every EV endpoint → all EVs OFF.
  - `2.6 MW < P < 4.8 MW`: sends `[210, 200, 210, 200, 210, 200]` kW across the six registered endpoints (repeat-alternating if more exist), i.e., alternating 210 kW and 200 kW commands to every charger.
  - `P ≤ 2.6 MW`: turn **all EVs ON** using per-endpoint setpoints `[210, 200, 200, 200, 200, 206] kW` (the sixth endpoint is explicitly set to 206 kW in the script to slightly reduce that charger’s demand; falls back to 200 kW if more endpoints exist).
- Records time-aligned feeder load and EV setpoints, writing `1c_EV_Outputs.csv`; generates `output/1c_Feeder_and_EVs_subplot.png` summarizing feeder load and EV outputs.
- Finalizes by requesting max HELICS time, disconnecting, and destroying the federate.

**Secondary/demo controller (`1bc_EV_Controller_2.py`, config `1c_Control_2.json`)**
- Mirrors the HELICS setup but uses a shorter demo loop (`total_interval = 1` with 60 s steps) and limits of 2.6 MW / 4.2 MW.
  - Actions:
    - overload → all EVs OFF
    - safe band (2.6–4.2 MW) → the first two endpoints (EV1/EV2, identifiers `m0` and `m1`) are set to 210 kW while other endpoints remain at their last values (or defaults if none were set)
    - low load → all EVs set to 200 kW
- Optionally plots live matplotlib subplots; saves results to `1c_EV_Outputs_2.csv` before finalizing the federate.

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


**Assumption:** For EV CS 3–6, we assume a specific attack window during the peak demand period (15:00–17:00 PM), since their powers vary dynamically over time.
