# Grid Simulation Models

This repository contains simulation models for power grid co-simulation using HELICS (Hierarchical Engine for Large-scale Infrastructure Co-Simulation) and GridLAB-D.

## Overview

The models in this repository demonstrate transmission and distribution (T&D) co-simulation capabilities, including:

- **GridLAB-D**: Distribution system simulation with IEEE test feeders
- **GridPACK**: Transmission system power flow analysis
- **HELICS**: Co-simulation framework for coupling multiple simulators
- **EV Integration**: Electric vehicle charging controllers and load scheduling

## Directory Structure

- `2bus-13bus/`: Main simulation directory containing:
  - GridLAB-D models (IEEE 13-bus, IEEE 123-bus feeders)
  - GridPACK transmission models
  - EV controller Python scripts
  - HELICS configuration files
  - Build files and simulation outputs

## Components

### Distribution System Models
- IEEE 13-bus test feeder
- IEEE 123-bus test feeder
- IEEE 8500-node test feeder

### Transmission System Models
- 2-bus transmission system
- 300-bus transmission network

### Co-simulation Features
- Real-time data exchange between transmission and distribution systems
- EV charging coordination
- Load scheduling and control

## Requirements

- HELICS framework
- GridLAB-D power distribution simulator
- GridPACK toolkit
- Python 3.x for control scripts
- CMake for building GridPACK components

## Usage

Refer to individual configuration files in the `2bus-13bus/` directory for specific simulation setups and execution instructions.