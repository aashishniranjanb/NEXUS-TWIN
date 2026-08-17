import random

def generate_route_file(filepath="simulation/routes/nexus.rou.xml", num_vehicles=1000, duration=1800, include_emergency: bool = True):
    random.seed(42)
    with open(filepath, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">\n')
        
        # Vehicle Types
        f.write('    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5.0" minGap="2.5" maxSpeed="13.89" color="0,0.8,1"/>\n')
        f.write('    <vType id="bus" accel="1.2" decel="4.0" sigma="0.5" length="12.0" minGap="3.0" maxSpeed="11.11" color="1,0.5,0"/>\n')
        f.write('    <vType id="truck" accel="1.0" decel="3.5" sigma="0.5" length="10.0" minGap="3.0" maxSpeed="10.00" color="0.8,0.2,0.8"/>\n')
        f.write('    <vType id="emergency" vClass="emergency" accel="3.5" decel="5.0" sigma="0.2" length="6.5" minGap="2.0" maxSpeed="20.00" color="1,0,0"/>\n')
        
        # Standard Corridor & Cross Routes
        f.write('    <route id="r_N_S" edges="N_to_J1 J1_to_J2 J2_to_J3 J3_to_S"/>\n')
        f.write('    <route id="r_S_N" edges="S_to_J3 J3_to_J2 J2_to_J1 J1_to_N"/>\n')
        f.write('    <route id="r_W1_E1" edges="W1_to_J1 J1_to_E1"/>\n')
        f.write('    <route id="r_E1_W1" edges="E1_to_J1 J1_to_W1"/>\n')
        f.write('    <route id="r_W2_E2" edges="W2_to_J2 J2_to_E2"/>\n')
        f.write('    <route id="r_E2_W2" edges="E2_to_J2 J2_to_W2"/>\n')
        f.write('    <route id="r_W3_E3" edges="W3_to_J3 J3_to_E3"/>\n')
        f.write('    <route id="r_E3_W3" edges="E3_to_J3 J3_to_W3"/>\n')
        f.write('    <route id="r_N_E2" edges="N_to_J1 J1_to_J2 J2_to_E2"/>\n')
        f.write('    <route id="r_W2_S" edges="W2_to_J2 J2_to_J3 J3_to_S"/>\n')

        # Bypass Routes for Diversion Strategy
        f.write('    <route id="r_bypass_E" edges="N_to_J1 J1_to_E1 E1_to_E2 E2_to_J2 J2_to_J3 J3_to_S"/>\n')
        f.write('    <route id="r_bypass_W" edges="N_to_J1 J1_to_W1 W1_to_W2 W2_to_J2 J2_to_J3 J3_to_S"/>\n')

        routes = ["r_N_S", "r_S_N", "r_W1_E1", "r_E1_W1", "r_W2_E2", "r_E2_W2", "r_W3_E3", "r_E3_W3", "r_N_E2", "r_W2_S"]
        weights = [25, 25, 8, 8, 12, 12, 4, 4, 1, 1]

        depart_times = sorted([random.uniform(1, duration) for _ in range(num_vehicles)])

        emergency_inserted = False
        emergency_depart_time = 300.0  # Insert emergency vehicle at t=300s

        for i, depart in enumerate(depart_times):
            # Optionally insert 1 emergency vehicle around t=300
            if include_emergency and not emergency_inserted and depart >= emergency_depart_time:
                f.write(f'    <vehicle id="veh_emergency" type="emergency" route="r_N_S" depart="{emergency_depart_time:.1f}" departLane="best" departSpeed="max"/>\n')
                emergency_inserted = True

            route_id = random.choices(routes, weights=weights)[0]
            
            # 85% cars, 10% buses, 5% trucks
            vtype_roll = random.random()
            if vtype_roll < 0.85:
                vtype = "car"
            elif vtype_roll < 0.95:
                vtype = "bus"
            else:
                vtype = "truck"

            f.write(f'    <vehicle id="veh_{i}" type="{vtype}" route="{route_id}" depart="{depart:.1f}" departLane="best" departSpeed="max"/>\n')

        f.write('</routes>\n')

if __name__ == "__main__":
    generate_route_file()
    print("Generated nexus.rou.xml with 1000 vehicles + emergency vehicle.")
