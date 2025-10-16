# 2bus-13bus Grid Simulation - Detailed Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    T&D Co-Simulation Architecture                            │
│                                                                               │
│  Transmission (GridPACK)          Distribution (GridLAB-D)                   │
│  IEEE 9-bus System                IEEE 123-node Feeders                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Transmission System (GridPACK - IEEE 9-bus)

```
                    GridPACK Federate: "gridpack"

    ┌────────┐                                    ┌────────┐
    │  Gen1  │                                    │  Gen2  │
    └───┬────┘                                    └────┬───┘
        │                                              │
        │ Bus1                                    Bus2 │
        ○──────────────Line 1-4────────────────────────○ ← Tie to Feeder A
        │                                              │   (Node650)
        │                                              │
    Bus4○                                         Bus5 ○
        │                                              │
        │                                              │
    Bus7○──────────────Line 7-8──────────────○ Bus8   │
        │                                     │        │
        │                                     │        │
    Bus9○                                     │    Bus6○
        │                                     │        │
        └─────────────Line 9-6─────────────────────────┘
                                              │
                                         Bus3 ○ ← Tie to Feeder B
                                              │   (Node650)
                                         ┌────┴────┐
                                         │  Gen3   │
                                         └─────────┘

    Publications:
    - gridpack/Va, gridpack/Vb, gridpack/Vc (complex voltage at tie buses)

    Subscriptions:
    - gld_hlc_conn/Sa, Sb, Sc (power demand from feeders)
```

---

## Distribution System A (GridLAB-D - IEEE 123-node)

**Federate**: `IEEE13bus_fed`
**Config**: `1c_IEEE_123_feeder.glm`
**Swing Bus**: `Node650` (connected to Transmission Bus2)

### Main Feeder Topology

```
                        From Transmission Bus2
                               ↓
                          [Node650] ← Swing Bus (3-phase)
                               │    Publications: gld_hlc_conn/Sa,Sb,Sc
                               │    Subscriptions: gridpack/Va,Vb,Vc
                               │
                          [Regulator]
                               │
                         ┌─────┴─────┐
                         │           │
                    [Primary  ]  [Laterals...]
                      Feeder
                         │
                    ┌────┴────┬──────┬──────┬──────┬──────┐
                    │         │      │      │      │      │
                   l5        l2    l88    l92   l107   l114
                    │         │      │      │      │      │
                [swEV1]   [swEV2] [swEV3][swEV4][swEV5][swEV6]
                    │         │      │      │      │      │
                  [EV1]     [EV2]  [EV3]  [EV4]  [EV5]  [EV6]
                    │
              [swEV1_storage]
                    │
              [EV1_STORAGE] ← Battery (islanding capable)


              [swEV4_storage]
                    │
              [EV4_STORAGE] ← Battery (islanding capable)
```

### EV Charging Station Details

```
┌────────────────────────────────────────────────────────────────────────────┐
│ EV Station Configuration (Feeder A)                                        │
├────┬──────┬───────┬─────────┬─────────┬─────────────┬──────────────────────┤
│ ID │ Link │ Phase │ Switch  │ Storage │ Normal Max  │ Attack Max           │
├────┼──────┼───────┼─────────┼─────────┼─────────────┼──────────────────────┤
│EV1 │ l5   │ CN    │ swEV1   │ ✓ Yes   │ 220 kW      │ 4000 kW (4 MW)       │
│    │      │       │ +storage│         │             │                      │
├────┼──────┼───────┼─────────┼─────────┼─────────────┼──────────────────────┤
│EV2 │ l2   │ BN    │ swEV2   │ ✗ No    │ 200 kW      │ 4000 kW (4 MW)       │
├────┼──────┼───────┼─────────┼─────────┼─────────────┼──────────────────────┤
│EV3 │ l88  │ AN    │ swEV3   │ ✗ No    │ 200 kW      │ 4000 kW (4 MW)       │
├────┼──────┼───────┼─────────┼─────────┼─────────────┼──────────────────────┤
│EV4 │ l92  │ CN    │ swEV4   │ ✓ Yes   │ 220 kW      │ 4000 kW (4 MW)       │
│    │      │       │ +storage│         │             │                      │
├────┼──────┼───────┼─────────┼─────────┼─────────────┼──────────────────────┤
│EV5 │ l107 │ BN    │ swEV5   │ ✗ No    │ 200 kW      │ 4000 kW (4 MW)       │
├────┼──────┼───────┼─────────┼─────────┼─────────────┼──────────────────────┤
│EV6 │ l114 │ AN    │ swEV6   │ ✗ No    │ 200 kW      │ 4000 kW (4 MW)       │
└────┴──────┴───────┴─────────┴─────────┴─────────────┴──────────────────────┘

Phase Distribution:
- Phase A (AN): EV3, EV6
- Phase B (BN): EV2, EV5
- Phase C (CN): EV1, EV4 (both have battery storage)
```

### Islanding Capability (EV1 and EV4)

```
Normal Operation:                     Islanded Operation (Overload):

Grid ──[swEV1]──○──[EV1]             Grid  [swEV1]    ○──[EV1]
        CLOSED   │                           OPEN      │
                 │                                     │
    [swEV1_storage]                         [swEV1_storage]
        OPEN     │                             CLOSED  │
                 │                                     │
            [Battery]                             [Battery]
                                                  (powers EV1)

Trigger: Total feeder load > 4.2 MW
Action: Legitimate controller opens grid switch, closes storage switch
Result: EV1/EV4 powered by local battery, isolated from grid
```

---

## Distribution System B (GridLAB-D - IEEE 123-node)

**Federate**: `IEEE13bus_fed_2`
**Config**: `1c_IEEE_123_feeder_2.glm`
**Swing Bus**: `Node650` (connected to Transmission Bus3)

```
                        From Transmission Bus3
                               ↓
                          [Node650] ← Swing Bus (3-phase)
                               │
                          [Regulator]
                               │
                         [IEEE 123-node]
                          Distribution
                           Network

    ⚠️  No EV control configured for Feeder B
    ⚠️  Used for load diversity / system testing
```

---

## HELICS Communication Architecture

### Federate Topology

```
                         ┌─────────────────┐
                         │  HELICS Broker  │
                         │  Port: 23406    │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┬───────────────┐
              │                   │                   │               │
              │                   │                   │               │
    ┌─────────▼──────┐  ┌────────▼────────┐  ┌──────▼──────┐  ┌────▼────────┐
    │   gridpack     │  │ IEEE13bus_fed   │  │IEEE13bus_   │  │EVController │
    │                │  │                 │  │   fed_2     │  │    Sim      │
    │ Transmission   │  │ Distribution A  │  │Distribution │  │             │
    │ IEEE 9-bus     │  │ IEEE 123-node   │  │     B       │  │ Legitimate  │
    │                │  │ + 6 EVs         │  │ IEEE 123    │  │ Controller  │
    └────────────────┘  └─────────────────┘  └─────────────┘  └─────────────┘
              │                   │                                   │
              │ Publishes:        │ Publishes:                        │ Publishes:
              │ gridpack/Va,Vb,Vc │ gld_hlc_conn/Sa,Sb,Sc             │ swEV1,swEV4
              │                   │                                   │ swEV1_storage
              │ Subscribes:       │ Subscribes:                       │ swEV4_storage
              │ gld_hlc_conn/     │ gridpack/Va,Vb,Vc                 │
              │   Sa,Sb,Sc        │ swEV1,swEV4 (switches)            │ Subscribes:
              │                   │                                   │ gld_hlc_conn/
              │                   │ EV Endpoints (bidirectional):     │   Sa,Sb,Sc
              │                   │ gld_hlc_conn/EV1-6 ←─────────────────┐
              │                   │                                   │  │
              │                   │                                   ▼  │
              │                   │                         ┌─────────────┴──────┐
              │                   │                         │ EV Attacker MCP    │
              │                   │                         │ (ev_attacker_mcp)  │
              │                   │                         │                    │
              │                   │                         │ Publishes:         │
              │                   │                         │ attacker/EV1-6 ────┤
              │                   │                         │ (to same dest as   │
              │                   │                         │  controller!)      │
              │                   │                         │                    │
              │                   │                         │ Subscribes:        │
              │                   │                         │ gld_hlc_conn/Sa,Sb,│
              │                   │                         │   Sc (feeder load) │
              │                   │                         │ gridpack/Va,Vb,Vc  │
              │                   │                         │ swEV1,swEV4,etc    │
              │                   │                         └────────────────────┘
              │                   │                                   │
              └───────────────────┴───────────────────────────────────┘
                            HELICS Message Bus
```

### Message Flow: EV Setpoint Control

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Competing Controllers (Red Team vs Blue Team)                            │
└──────────────────────────────────────────────────────────────────────────┘

Legitimate Controller Path:
┌─────────────────┐  Monitors    ┌──────────────────┐
│ EVControllerSim │ ──────────→  │ gld_hlc_conn/Sa  │ ← Feeder load
└────────┬────────┘              │      Sb, Sc      │
         │                       └──────────────────┘
         │ Decides setpoint
         │ (peak shaving logic)
         │
         │ Publishes every 1200s
         ▼
┌────────────────────────┐
│ EV_Controller/EV1-6    │ ─────┐
└────────────────────────┘      │
                                │ Both send to:
Attack Controller Path:         │ gld_hlc_conn/EV1-6
┌─────────────────┐             │
│ ev_attacker_mcp │             │
└────────┬────────┘             │
         │                      │
         │ AI attack decision   │
         │ (malicious setpoint) │
         │                      │
         │ Publishes as needed  │
         ▼                      │
┌────────────────────────┐      │
│   attacker/EV1-6       │ ─────┘
└────────────────────────┘
         │
         │ HELICS delivers chronologically
         ▼
┌────────────────────────┐
│  gld_hlc_conn/EV1-6    │ ← GridLAB-D endpoint
└────────┬───────────────┘
         │ Last message wins!
         ▼
┌────────────────────────┐
│ EV1-6 Load Objects     │ ← constant_power_A/B/C property
│ in GridLAB-D           │
└────────────────────────┘
```

---

## Attack Surface Map

### Primary Attack Targets

```
┌────────────────────────────────────────────────────────────────────┐
│ Attack Surface Layer 1: EV Charging Stations                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Target: gld_hlc_conn/EV1-6 endpoints                             │
│  Method: Inject malicious setpoints via attacker MCP              │
│  Impact: Overload, phase imbalance, reverse power injection       │
│                                                                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │  EV3/6  │  │  EV2/5  │  │  EV1/4  │  │ Storage │              │
│  │ Phase A │  │ Phase B │  │ Phase C │  │ Systems │              │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘              │
│      ↑             ↑             ↑            ↑                   │
│      └─────────────┴─────────────┴────────────┘                   │
│                    Attack Vectors:                                │
│                    - Overload (2-4 MW)                            │
│                    - Phase imbalance                              │
│                    - Reverse power (-500 kW)                      │
│                    - Storage depletion                            │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ Attack Surface Layer 2: Distribution Feeder                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Critical Point: Node650 (swing bus)                              │
│  Protection: Feeder load limits (2.6-4.2 MW)                      │
│  Vulnerability: Cumulative EV overload                            │
│                                                                    │
│         [Node650] ← Swing Bus                                     │
│             │                                                      │
│             ├──→ Normal Load: ~3.0 MW                             │
│             ├──→ EV Load: 0-1.2 MW (6 EVs × 200 kW)              │
│             └──→ Attack Load: Up to 24 MW! (6 EVs × 4 MW)        │
│                                                                    │
│  Attack Goal: Total > 4.2 MW → Trigger protection                 │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ Attack Surface Layer 3: Transmission Tie                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Weak Point: Bus2 ↔ Node650 tie                                  │
│  Impact: Cascading to transmission system                         │
│  Detection: Voltage deviation at gridpack/Va,Vb,Vc               │
│                                                                    │
│    [Transmission Bus2]                                            │
│             ↕ Tie line                                            │
│      [Node650 Feeder A]                                           │
│                                                                    │
│  Attack Strategy: Stress distribution → propagate to transmission │
└────────────────────────────────────────────────────────────────────┘
```

---

## Control Flow: Normal vs Attack Mode

### Normal Operation (Blue Team)

```
Time    │ Legitimate Controller Actions
─────────┼──────────────────────────────────────────────────────
0s      │ Monitor: gld_hlc_conn/Sa,Sb,Sc
        │ Total load: 3.0 MW
        │ Decision: Normal operation
        │ Action: EV1-6 → 200-220 kW each
─────────┼──────────────────────────────────────────────────────
1200s   │ Monitor: Total load 3.5 MW
(20min) │ Decision: Safe range
        │ Action: EV1-2 → 210 kW (mild reduction)
─────────┼──────────────────────────────────────────────────────
2400s   │ Monitor: Total load 4.3 MW (OVERLOAD!)
(40min) │ Decision: Trigger islanding
        │ Actions:
        │   - Open swEV1, swEV4 (disconnect from grid)
        │   - Close swEV1_storage, swEV4_storage
        │   - Set EV1, EV4 → 200 kW (battery powered)
        │   - Set EV2-6 → 0 kW (disconnected)
```

### Attack Operation (Red Team)

```
Time    │ Attacker MCP Actions
─────────┼──────────────────────────────────────────────────────
0s      │ Observe: get_grid_status
        │ Total load: 3.0 MW
        │ Plan: Wait for peak demand window
─────────┼──────────────────────────────────────────────────────
900s    │ Observe: Total load 3.8 MW (approaching peak)
(15min) │ Decision: Execute overload attack
        │ Action:
        │   - EV3 → 2500 kW (overload_attack)
        │   - EV5 → 2000 kW (overload_attack)
        │ Result: Total load → 8.3 MW (CRITICAL!)
─────────┼──────────────────────────────────────────────────────
920s    │ Legitimate controller responds:
        │   - Detects overload
        │   - Triggers islanding (too late?)
        │ Attacker continues:
        │   - EV1 → 220 kW (drain battery in island mode)
        │   - EV4 → 220 kW (drain battery in island mode)
─────────┼──────────────────────────────────────────────────────
1800s   │ Result:
(30min) │   - Batteries depleted
        │   - EV1/EV4 lose power
        │   - Grid stressed, possible cascading failure
```

---

## Physical Grid Layout (Simplified)

```
                          ═══════════════════════
                          ║  Transmission Grid  ║
                          ║   (IEEE 9-bus)      ║
                          ║   69 kV             ║
                          ═══════════════════════
                                     │
                          ┌──────────┴──────────┐
                          │                     │
                    [Transformer]         [Transformer]
                      69kV/4.16kV           69kV/4.16kV
                          │                     │
                    ┌─────┴─────┐         ┌─────┴─────┐
                    │ Node650   │         │ Node650   │
                    │ Feeder A  │         │ Feeder B  │
                    └─────┬─────┘         └───────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
         [Regulator]  [Capacitor] [Switches]
              │
    ┌─────────┴─────────┬─────────┬─────────┐
    │                   │         │         │
[Primary Lines]    [Laterals] [Laterals] [Transformers]
    │                   │         │         │
    │              Single-phase distribution
    │              480V / 240V / 120V
    │
    ├─→ l5   ─→ [EV1] 200kW → Phase C
    ├─→ l2   ─→ [EV2] 200kW → Phase B
    ├─→ l88  ─→ [EV3] 200kW → Phase A
    ├─→ l92  ─→ [EV4] 200kW → Phase C
    ├─→ l107 ─→ [EV5] 200kW → Phase B
    └─→ l114 ─→ [EV6] 200kW → Phase A

    Residential/Commercial Loads: ~3.0 MW total
    EV Load (normal): ~1.2 MW total (6 × 200kW)
    Total Normal: ~4.2 MW (at upper protection limit)
```

---

## Legend

```
Symbols:
  ○ ═ ─    Electrical connections
  [ ]      Equipment/component
  ↔ ↕ →    Power/data flow
  ┌ ┐ └ ┘  Diagram structure

Components:
  Node     - Bus bar (voltage node)
  Link     - Distribution line segment
  Transformer - Voltage conversion
  Switch   - Controllable breaker
  Load     - Power consumption point

HELICS:
  Publication   - Data sent to HELICS bus
  Subscription  - Data received from HELICS bus
  Endpoint      - Bidirectional message channel

Protection:
  Relay    - Automatic protection device
  Limit    - Threshold for protection activation
  Margin   - Distance from protection threshold
```

---

## Summary Statistics

```
┌────────────────────────────────────────────────────────────┐
│ Grid Model Statistics                                      │
├──────────────────────────┬─────────────────────────────────┤
│ Transmission Buses       │ 9 (IEEE 9-bus standard)         │
│ Distribution Nodes (A)   │ 123 (IEEE 123-node standard)    │
│ Distribution Nodes (B)   │ 123 (IEEE 123-node standard)    │
│ EV Charging Stations     │ 6 (Feeder A only)               │
│ Battery Storage Systems  │ 2 (EV1, EV4)                    │
│ HELICS Federates         │ 5 (includes attacker MCP)       │
│ Total Attack Endpoints   │ 6 (gld_hlc_conn/EV1-6)          │
│ Protection Limits        │ 2.6 MW - 4.2 MW                 │
│ Normal Peak Load         │ ~4.0 MW                         │
│ Maximum Attack Load      │ 24 MW (6 × 4 MW)                │
└──────────────────────────┴─────────────────────────────────┘
```

---

**Document Version**: 1.0
**Last Updated**: 2025-01-07
**Purpose**: Defensive cybersecurity research and AI-driven grid attack simulation
