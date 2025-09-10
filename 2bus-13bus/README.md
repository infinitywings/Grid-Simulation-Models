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