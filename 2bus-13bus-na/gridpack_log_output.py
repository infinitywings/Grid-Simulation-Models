import re

log_file_path = 'gridpack.log'  # Replace with your actual file name

# Store the data in a list of dicts per iteration
iterations_data = []

with open(log_file_path, 'r') as file:
    lines = file.readlines()

i = 0
while i < len(lines):
    line = lines[i]
    
    # Detect iteration header
    if line.startswith("Iteration"):
        iteration_num = int(re.search(r"Iteration\s+(\d+)", line).group(1))
        iteration_info = {"iteration": iteration_num, "buses": []}
        
        # Look for the bus voltage section
        while i < len(lines) and not lines[i].strip().startswith("Bus Voltages and Phase Angles"):
            i += 1
        
        i += 2  # Skip the header lines under "Bus Voltages and Phase Angles"

        # Read bus values
        while i < len(lines) and lines[i].strip() != "":
            match = re.match(r"\s*(\d+)\s+([-.\d]+)\s+([-.\d]+)", lines[i])
            if match:
                bus_num = int(match.group(1))
                phase_angle = float(match.group(2))
                voltage_mag = float(match.group(3))
                iteration_info["buses"].append({
                    "bus": bus_num,
                    "voltage_mag": voltage_mag,
                    "phase_angle": phase_angle
                })
            i += 1

        iterations_data.append(iteration_info)
    
    i += 1

# Example: print results for each iteration
for it in iterations_data:
    print(f"Iteration {it['iteration']}")
    for bus in it["buses"]:
        print(f"Bus {bus['bus']}: V = {bus['voltage_mag']}, θ = {bus['phase_angle']}")
    print()
