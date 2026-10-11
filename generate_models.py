import os
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

os.makedirs("models", exist_ok=True)

def create_pbr(color_rgba, metallic=0.2, roughness=0.5):
    """Helper to create PBR material with RGBA color."""
    return PBRMaterial(
        baseColorFactor=color_rgba,
        metallicFactor=float(metallic),
        roughnessFactor=float(roughness)
    )

def create_ring_geometry(outer_r, inner_r, height, sections=64):
    """Creates a 3D hollow ring/torus frame."""
    theta = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    
    # Outer cylinder vertices
    vo_top = np.column_stack([outer_r * np.cos(theta), outer_r * np.sin(theta), np.full(sections, height / 2)])
    vo_bot = np.column_stack([outer_r * np.cos(theta), outer_r * np.sin(theta), np.full(sections, -height / 2)])
    
    # Inner cylinder vertices
    vi_top = np.column_stack([inner_r * np.cos(theta), inner_r * np.sin(theta), np.full(sections, height / 2)])
    vi_bot = np.column_stack([inner_r * np.cos(theta), inner_r * np.sin(theta), np.full(sections, -height / 2)])
    
    verts = np.vstack([vo_top, vo_bot, vi_top, vi_bot])
    faces = []
    
    for i in range(sections):
        next_i = (i + 1) % sections
        
        # Outer wall (quad -> 2 tris)
        faces.append([i, next_i, sections + next_i])
        faces.append([i, sections + next_i, sections + i])
        
        # Inner wall (quad -> 2 tris, reverse orientation)
        faces.append([2 * sections + next_i, 2 * sections + i, 3 * sections + i])
        faces.append([2 * sections + next_i, 3 * sections + i, 3 * sections + next_i])
        
        # Top cap
        faces.append([i, 2 * sections + i, 2 * sections + next_i])
        faces.append([i, 2 * sections + next_i, next_i])
        
        # Bottom cap
        faces.append([sections + next_i, 3 * sections + next_i, 3 * sections + i])
        faces.append([sections + next_i, 3 * sections + i, sections + i])
        
    mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)
    return mesh

# ==========================================
# 1. CLINOSTAT 3D MODEL
# ==========================================
def generate_clinostat():
    print("Generating Clinostat 3D model...")
    scene = trimesh.Scene()
    
    # Materials
    mat_base = create_pbr([0.15, 0.18, 0.22, 1.0], metallic=0.7, roughness=0.3)
    mat_pillar = create_pbr([0.7, 0.75, 0.8, 1.0], metallic=0.9, roughness=0.2)
    mat_outer_ring = create_pbr([0.06, 0.65, 0.35, 1.0], metallic=0.8, roughness=0.25) # Emerald Green (Axis 1)
    mat_inner_ring = create_pbr([0.85, 0.2, 0.22, 1.0], metallic=0.8, roughness=0.25) # Crimson Red (Axis 2)
    mat_motor = create_pbr([0.18, 0.2, 0.22, 1.0], metallic=0.6, roughness=0.4)
    mat_shaft = create_pbr([0.85, 0.7, 0.2, 1.0], metallic=0.9, roughness=0.1) # Brass
    mat_chamber = create_pbr([0.7, 0.85, 0.95, 0.7], metallic=0.1, roughness=0.1) # Transparent acrylic
    mat_substrate = create_pbr([0.22, 0.16, 0.12, 1.0], metallic=0.0, roughness=0.9) # Dark soil
    mat_plant = create_pbr([0.15, 0.85, 0.25, 1.0], metallic=0.1, roughness=0.4) # Sprout green
    mat_led = create_pbr([0.95, 0.2, 0.75, 1.0], metallic=0.2, roughness=0.2) # Phyto magenta

    # 1. Base Plate & Feet
    base = trimesh.creation.box([160, 220, 10])
    base.apply_translation([0, 0, 5])
    base.visual.material = mat_base
    scene.add_geometry(base, node_name="Base_Plate")

    # Anti-vibration rubber feet
    for dx in [-65, 65]:
        for dy in [-95, 95]:
            foot = trimesh.creation.cylinder(radius=8, height=6)
            foot.apply_translation([dx, dy, -3])
            foot.visual.material = create_pbr([0.05, 0.05, 0.05, 1.0], metallic=0.1, roughness=0.8)
            scene.add_geometry(foot, node_name=f"Foot_{dx}_{dy}")

    # 2. Vertical Support Towers
    for dy in [-85, 85]:
        pillar = trimesh.creation.box([16, 16, 120])
        pillar.apply_translation([0, dy, 70])
        pillar.visual.material = mat_pillar
        scene.add_geometry(pillar, node_name=f"Support_Pillar_{dy}")
        
        bearing = trimesh.creation.cylinder(radius=14, height=12)
        bearing.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
        bearing.apply_translation([0, dy, 130])
        bearing.visual.material = mat_base
        scene.add_geometry(bearing, node_name=f"Bearing_{dy}")

    # 3. Outer Gimbal Ring (Axis 1 - Emerald Green)
    outer_ring = create_ring_geometry(outer_r=70, inner_r=62, height=10)
    # Rotate ring so its plane is vertical (XZ plane) and pivots along Y-axis
    outer_ring.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    outer_ring.apply_translation([0, 0, 130])
    outer_ring.visual.material = mat_outer_ring
    scene.add_geometry(outer_ring, node_name="Outer_Ring_Axis1")

    # Outer pivot shafts (along Y axis)
    for dy in [-80, 80]:
        shaft = trimesh.creation.cylinder(radius=4, height=18)
        shaft.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
        shaft.apply_translation([0, dy, 130])
        shaft.visual.material = mat_shaft
        scene.add_geometry(shaft, node_name=f"Outer_Shaft_{dy}")

    # Stepper Motor 1 (Axis 1 Drive, NEMA 17 style)
    motor1_body = trimesh.creation.box([38, 38, 38])
    motor1_body.apply_translation([0, 108, 130])
    motor1_body.visual.material = mat_motor
    scene.add_geometry(motor1_body, node_name="Stepper_Motor_1")
    
    motor1_cap = trimesh.creation.cylinder(radius=10, height=8)
    motor1_cap.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    motor1_cap.apply_translation([0, 86, 130])
    motor1_cap.visual.material = mat_shaft
    scene.add_geometry(motor1_cap, node_name="Motor1_Coupler")

    # 4. Inner Gimbal Ring (Axis 2 - Crimson Red)
    inner_ring = create_ring_geometry(outer_r=55, inner_r=48, height=8)
    # Pivot along Z or X axis (perpendicular to Axis 1)
    inner_ring.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    inner_ring.apply_translation([0, 0, 130])
    inner_ring.visual.material = mat_inner_ring
    scene.add_geometry(inner_ring, node_name="Inner_Ring_Axis2")

    # Stepper Motor 2 (Axis 2 Drive)
    motor2_body = trimesh.creation.box([28, 28, 28])
    motor2_body.apply_translation([68, 0, 130])
    motor2_body.visual.material = mat_motor
    scene.add_geometry(motor2_body, node_name="Stepper_Motor_2")

    # 5. Central Plant Capsule (Cassette with seeds & substrate)
    capsule = trimesh.creation.box([38, 38, 28])
    capsule.apply_translation([0, 0, 130])
    capsule.visual.material = mat_chamber
    scene.add_geometry(capsule, node_name="Growth_Capsule_Transparent")

    # Substrate block inside capsule
    substrate = trimesh.creation.box([34, 34, 10])
    substrate.apply_translation([0, 0, 122])
    substrate.visual.material = mat_substrate
    scene.add_geometry(substrate, node_name="Nutrient_Substrate")

    # Radish seeds / sprouts inside
    for sx in [-8, 0, 8]:
        for sy in [-8, 0, 8]:
            sprout_stem = trimesh.creation.cylinder(radius=1.0, height=10)
            sprout_stem.apply_translation([sx, sy, 132])
            sprout_stem.visual.material = mat_plant
            scene.add_geometry(sprout_stem, node_name=f"Sprout_Stem_{sx}_{sy}")

            leaf = trimesh.creation.box([5, 3, 1])
            leaf.apply_translation([sx, sy, 138])
            leaf.visual.material = mat_plant
            scene.add_geometry(leaf, node_name=f"Leaf_{sx}_{sy}")

    # Top Phyto-LED bar
    led_bar = trimesh.creation.box([32, 6, 3])
    led_bar.apply_translation([0, 0, 142])
    led_bar.visual.material = mat_led
    scene.add_geometry(led_bar, node_name="Phyto_LED_Bar")

    output_path = "models/clinostat_2axis.glb"
    scene.export(output_path)
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

# ==========================================
# 2. ARDUINO BIOREACTOR 3D MODEL
# ==========================================
def generate_arduino_bioreactor():
    print("Generating Arduino Bioreactor 3D model...")
    scene = trimesh.Scene()

    # Materials
    mat_pcb_arduino = create_pbr([0.0, 0.42, 0.48, 1.0], metallic=0.2, roughness=0.4) # Arduino Teal
    mat_pcb_relay = create_pbr([0.1, 0.35, 0.75, 1.0], metallic=0.2, roughness=0.4) # Blue Relay PCB
    mat_relay_cube = create_pbr([0.1, 0.45, 0.85, 1.0], metallic=0.3, roughness=0.3) # Songle Relay Blue
    mat_chip = create_pbr([0.1, 0.1, 0.12, 1.0], metallic=0.1, roughness=0.6) # ATmega328P
    mat_metal = create_pbr([0.85, 0.85, 0.9, 1.0], metallic=0.9, roughness=0.15) # Chrome/Tin
    mat_headers = create_pbr([0.08, 0.08, 0.08, 1.0], metallic=0.1, roughness=0.7) # Black headers
    mat_sensor_white = create_pbr([0.92, 0.92, 0.94, 1.0], metallic=0.1, roughness=0.4) # DHT22 white casing
    mat_oled_glass = create_pbr([0.05, 0.1, 0.25, 1.0], metallic=0.5, roughness=0.1) # OLED glass
    mat_fan = create_pbr([0.15, 0.15, 0.18, 1.0], metallic=0.3, roughness=0.5) # Fan plastic
    mat_pump = create_pbr([0.8, 0.82, 0.85, 1.0], metallic=0.7, roughness=0.3) # Mini pump metal
    mat_wire_red = create_pbr([0.9, 0.1, 0.1, 1.0], metallic=0.1, roughness=0.5)
    mat_wire_blue = create_pbr([0.1, 0.3, 0.9, 1.0], metallic=0.1, roughness=0.5)
    mat_gold = create_pbr([0.9, 0.75, 0.2, 1.0], metallic=0.8, roughness=0.2)

    # 1. Main Base Mounting Plate
    base = trimesh.creation.box([220, 180, 6])
    base.apply_translation([0, 0, 3])
    base.visual.material = create_pbr([0.08, 0.1, 0.14, 1.0], metallic=0.5, roughness=0.3)
    scene.add_geometry(base, node_name="Chassis_Mount_Board")

    # 2. Arduino Uno R3 Board
    ard_pos = [-45, -30, 8]
    ard_pcb = trimesh.creation.box([68.6, 53.4, 2.0])
    ard_pcb.apply_translation([ard_pos[0], ard_pos[1], ard_pos[2]])
    ard_pcb.visual.material = mat_pcb_arduino
    scene.add_geometry(ard_pcb, node_name="Arduino_Uno_PCB")

    # USB Port (Metal box)
    usb = trimesh.creation.box([16, 12, 11])
    usb.apply_translation([ard_pos[0] - 28, ard_pos[1] + 16, ard_pos[2] + 6.5])
    usb.visual.material = mat_metal
    scene.add_geometry(usb, node_name="Arduino_USB_Port")

    # DC Barrel Jack (Black cylinder + center pin)
    barrel = trimesh.creation.box([14, 9, 11])
    barrel.apply_translation([ard_pos[0] - 28, ard_pos[1] - 17, ard_pos[2] + 6.5])
    barrel.visual.material = mat_headers
    scene.add_geometry(barrel, node_name="Arduino_Power_Barrel")

    # ATmega328P DIP IC Chip
    chip = trimesh.creation.box([35, 8, 4])
    chip.apply_translation([ard_pos[0] + 5, ard_pos[1] - 8, ard_pos[2] + 3])
    chip.visual.material = mat_chip
    scene.add_geometry(chip, node_name="ATmega328P_Microcontroller")

    # Female Pin Header strips (Top & Bottom)
    for hy in [-23, 23]:
        h_strip = trimesh.creation.box([50, 4, 8])
        h_strip.apply_translation([ard_pos[0] + 6, ard_pos[1] + hy, ard_pos[2] + 5])
        h_strip.visual.material = mat_headers
        scene.add_geometry(h_strip, node_name=f"Arduino_Header_{hy}")

    # 3. 4-Channel Relay Module (Right side)
    relay_pos = [55, -25, 8]
    relay_pcb = trimesh.creation.box([75, 55, 2.0])
    relay_pcb.apply_translation([relay_pos[0], relay_pos[1], relay_pos[2]])
    relay_pcb.visual.material = mat_pcb_relay
    scene.add_geometry(relay_pcb, node_name="Relay_Module_PCB")

    # 4 Relay Blue Cubes
    for idx, ry in enumerate(np.linspace(-18, 18, 4)):
        cube = trimesh.creation.box([19, 11, 15])
        cube.apply_translation([relay_pos[0] - 5, relay_pos[1] + ry, relay_pos[2] + 8.5])
        cube.visual.material = mat_relay_cube
        scene.add_geometry(cube, node_name=f"Relay_Channel_{idx+1}")

        # Terminal block for wiring
        term = trimesh.creation.box([12, 10, 10])
        term.apply_translation([relay_pos[0] + 24, relay_pos[1] + ry, relay_pos[2] + 6])
        term.visual.material = create_pbr([0.1, 0.6, 0.2, 1.0], metallic=0.1, roughness=0.6) # Green terminal
        scene.add_geometry(term, node_name=f"Relay_Terminal_{idx+1}")

        # Active LED
        led = trimesh.creation.cylinder(radius=1.2, height=2)
        led.apply_translation([relay_pos[0] - 22, relay_pos[1] + ry, relay_pos[2] + 2])
        led.visual.material = create_pbr([0.95, 0.2, 0.1, 1.0], metallic=0.1, roughness=0.2)
        scene.add_geometry(led, node_name=f"Relay_LED_{idx+1}")

    # 4. DHT22 Sensor (Top Left)
    dht_pos = [-65, 55, 8]
    dht = trimesh.creation.box([15, 20, 8])
    dht.apply_translation([dht_pos[0], dht_pos[1], dht_pos[2] + 4])
    dht.visual.material = mat_sensor_white
    scene.add_geometry(dht, node_name="DHT22_Temp_Humidity_Sensor")

    # 5. OLED Display 0.96" SSD1306
    oled_pos = [-15, 55, 8]
    oled_board = trimesh.creation.box([28, 28, 1.5])
    oled_board.apply_translation([oled_pos[0], oled_pos[1], oled_pos[2]])
    oled_board.visual.material = mat_chip
    scene.add_geometry(oled_board, node_name="OLED_Board")

    oled_screen = trimesh.creation.box([24, 14, 1.0])
    oled_screen.apply_translation([oled_pos[0], oled_pos[1], oled_pos[2] + 1.2])
    oled_screen.visual.material = mat_oled_glass
    scene.add_geometry(oled_screen, node_name="OLED_Display_Screen")

    # 6. Capacitive Soil Moisture Sensor (Bottom-to-Top probe shape)
    soil_pos = [35, 55, 8]
    soil_pcb = trimesh.creation.box([16, 50, 1.6])
    soil_pcb.apply_translation([soil_pos[0], soil_pos[1], soil_pos[2]])
    soil_pcb.visual.material = create_pbr([0.1, 0.12, 0.14, 1.0], metallic=0.2, roughness=0.4)
    scene.add_geometry(soil_pcb, node_name="Soil_Moisture_Sensor_PCB")

    # 7. DC Cooling Fan (40mm)
    fan_pos = [85, 55, 8]
    fan_frame = trimesh.creation.box([40, 40, 12])
    fan_frame.apply_translation([fan_pos[0], fan_pos[1], fan_pos[2] + 6])
    fan_frame.visual.material = mat_fan
    scene.add_geometry(fan_frame, node_name="DC_Fan_40mm")

    fan_rotor = trimesh.creation.cylinder(radius=10, height=13)
    fan_rotor.apply_translation([fan_pos[0], fan_pos[1], fan_pos[2] + 6.5])
    fan_rotor.visual.material = mat_metal
    scene.add_geometry(fan_rotor, node_name="Fan_Motor_Hub")

    # 8. Mini Submersible Pump
    pump_pos = [-85, 0, 8]
    pump_cyl = trimesh.creation.cylinder(radius=12, height=36)
    pump_cyl.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    pump_cyl.apply_translation([pump_pos[0], pump_pos[1], pump_pos[2] + 12])
    pump_cyl.visual.material = mat_pump
    scene.add_geometry(pump_cyl, node_name="Mini_Water_Pump_3-6V")

    pump_nozzle = trimesh.creation.cylinder(radius=4, height=10)
    pump_nozzle.apply_translation([pump_pos[0] + 18, pump_pos[1], pump_pos[2] + 20])
    pump_nozzle.visual.material = mat_gold
    scene.add_geometry(pump_nozzle, node_name="Water_Pump_Outlet_Nozzle")

    output_path = "models/arduino_bioreactor.glb"
    scene.export(output_path)
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

# ==========================================
# 3. PLANT GRAVITROPISM COMPARISON 3D MODEL
# ==========================================
def generate_plant_gravitropism():
    print("Generating Plant Gravitropism Comparison 3D model...")
    scene = trimesh.Scene()

    # Materials
    mat_stand = create_pbr([0.1, 0.12, 0.16, 1.0], metallic=0.6, roughness=0.3)
    mat_plate = create_pbr([0.8, 0.9, 1.0, 0.5], metallic=0.1, roughness=0.1) # Glass dish
    mat_agar = create_pbr([0.22, 0.28, 0.18, 0.8], metallic=0.0, roughness=0.6) # Nutrient agar
    mat_root_normal = create_pbr([0.92, 0.9, 0.8, 1.0], metallic=0.1, roughness=0.5) # Cream root
    mat_root_disoriented = create_pbr([0.9, 0.85, 0.75, 1.0], metallic=0.1, roughness=0.5)
    mat_stem = create_pbr([0.3, 0.82, 0.25, 1.0], metallic=0.1, roughness=0.4)
    mat_leaf = create_pbr([0.15, 0.78, 0.2, 1.0], metallic=0.1, roughness=0.3)
    mat_radish_bulb = create_pbr([0.85, 0.15, 0.35, 1.0], metallic=0.2, roughness=0.4) # Magenta radish bulb

    # 1. Comparison Platform Stand
    stand = trimesh.creation.box([240, 130, 8])
    stand.apply_translation([0, 0, 4])
    stand.visual.material = mat_stand
    scene.add_geometry(stand, node_name="Lab_Comparison_Stand")

    # Name plaques for judges
    label_a = trimesh.creation.box([80, 20, 2])
    label_a.apply_translation([-60, -50, 9])
    label_a.visual.material = create_pbr([0.1, 0.6, 0.3, 1.0], metallic=0.5, roughness=0.3)
    scene.add_geometry(label_a, node_name="Label_GroupA_Control_1g")

    label_b = trimesh.creation.box([80, 20, 2])
    label_b.apply_translation([60, -50, 9])
    label_b.visual.material = create_pbr([0.8, 0.2, 0.3, 1.0], metallic=0.5, roughness=0.3)
    scene.add_geometry(label_b, node_name="Label_GroupB_Clinostat_Microg")

    # 2. Glass Dishes (Left: Group A 1g, Right: Group B Clinostat)
    for center_x, grp_name in [(-60, "GroupA_1g_Earth"), (60, "GroupB_Microgravity")]:
        dish = trimesh.creation.cylinder(radius=45, height=6)
        dish.apply_translation([center_x, 10, 10])
        dish.visual.material = mat_plate
        scene.add_geometry(dish, node_name=f"Culture_Dish_{grp_name}")

        agar = trimesh.creation.cylinder(radius=42, height=4)
        agar.apply_translation([center_x, 10, 12])
        agar.visual.material = mat_agar
        scene.add_geometry(agar, node_name=f"Agar_Substrate_{grp_name}")

    # ==========================
    # GROUP A: Normal Gravitropism (Roots straight DOWN, stems straight UP)
    # ==========================
    plant_coords_a = [(-75, 5), (-60, 20), (-45, 5), (-60, -5)]
    for idx, (px, py) in enumerate(plant_coords_a):
        # Small radish bulb / seed
        bulb = trimesh.creation.icosphere(subdivisions=2, radius=4.5)
        bulb.apply_translation([px, py, 18])
        bulb.visual.material = mat_radish_bulb
        scene.add_geometry(bulb, node_name=f"Bulb_A_{idx}")

        # Vertical Primary Taproot (Directly DOWNwards, gravitropism positive)
        root = trimesh.creation.cylinder(radius=1.5, height=22)
        root.apply_translation([px, py, 5])
        root.visual.material = mat_root_normal
        scene.add_geometry(root, node_name=f"Taproot_A_{idx}")

        # Lateral branch roots angling downward
        for angle, dz in [(0.4, -4), (-0.4, -10)]:
            branch = trimesh.creation.cylinder(radius=0.7, height=10)
            branch.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 1, 0]))
            branch.apply_translation([px + (angle*10), py, 8 + dz])
            branch.visual.material = mat_root_normal
            scene.add_geometry(branch, node_name=f"Root_Hair_A_{idx}_{dz}")

        # Vertical Stem (Hypocotyl) UPwards towards light
        stem = trimesh.creation.cylinder(radius=1.6, height=28)
        stem.apply_translation([px, py, 34])
        stem.visual.material = mat_stem
        scene.add_geometry(stem, node_name=f"Stem_A_{idx}")

        # Broad horizontal cotyledon leaves
        for leaf_angle in [0, np.pi]:
            leaf = trimesh.creation.box([14, 8, 1.2])
            leaf.apply_transform(trimesh.transformations.rotation_matrix(leaf_angle, [0, 0, 1]))
            leaf.apply_translation([px + (8 if leaf_angle==0 else -8), py, 48])
            leaf.visual.material = mat_leaf
            scene.add_geometry(leaf, node_name=f"Leaf_A_{idx}_{leaf_angle}")

    # ==========================
    # GROUP B: Clinostat Microgravity (Disoriented roots, curly loops, angular deviation)
    # ==========================
    plant_coords_b = [(45, 5), (60, 20), (75, 5), (60, -5)]
    for idx, (px, py) in enumerate(plant_coords_b):
        # Slightly deformed radish bulb
        bulb = trimesh.creation.icosphere(subdivisions=2, radius=4.2)
        bulb.apply_translation([px, py, 18])
        bulb.visual.material = mat_radish_bulb
        scene.add_geometry(bulb, node_name=f"Bulb_B_{idx}")

        # Disoriented curly root: series of angled segments showing curvature / spiraling
        prev_pt = np.array([px, py, 16], dtype=float)
        # Create zigzag / spiral points
        angle_offsets = [
            (5.0, 3.0, -4.0),
            (9.0, -4.0, -8.0),
            (4.0, -8.0, -10.0),
            (-3.0, -6.0, -6.0), # curving back sideways/upward!
            (-7.0, 2.0, -8.0)
        ]
        for seg_idx, (dx, dy, dz) in enumerate(angle_offsets):
            curr_pt = np.array([px + dx, py + dy, 18 + dz], dtype=float)
            vec = curr_pt - prev_pt
            length = np.linalg.norm(vec)
            if length > 0:
                seg = trimesh.creation.cylinder(radius=1.2 - seg_idx*0.15, height=length)
                # Align cylinder with vector
                cyl_axis = np.array([0, 0, 1])
                target_axis = vec / length
                rot_axis = np.cross(cyl_axis, target_axis)
                rot_angle = np.arccos(np.clip(np.dot(cyl_axis, target_axis), -1.0, 1.0))
                if np.linalg.norm(rot_axis) > 1e-6:
                    rot_axis /= np.linalg.norm(rot_axis)
                    seg.apply_transform(trimesh.transformations.rotation_matrix(rot_angle, rot_axis))
                mid_pt = (prev_pt + curr_pt) / 2.0
                seg.apply_translation(mid_pt)
                seg.visual.material = mat_root_disoriented
                scene.add_geometry(seg, node_name=f"CurlyRoot_B_{idx}_{seg_idx}")
            prev_pt = curr_pt

        # Wavy / inclined stem due to lack of gravity reference
        tilt_angle = 0.35 * (1 if idx % 2 == 0 else -1)
        stem = trimesh.creation.cylinder(radius=1.5, height=26)
        stem.apply_transform(trimesh.transformations.rotation_matrix(tilt_angle, [0, 1, 0]))
        stem.apply_translation([px + (tilt_angle*12), py, 32])
        stem.visual.material = mat_stem
        scene.add_geometry(stem, node_name=f"Stem_B_{idx}")

        # Tilted / asymmetric leaves
        for leaf_angle in [0.4, np.pi + 0.3]:
            leaf = trimesh.creation.box([13, 7, 1.2])
            leaf.apply_transform(trimesh.transformations.rotation_matrix(leaf_angle, [0, 0, 1]))
            leaf.apply_translation([px + (7 if leaf_angle < 2 else -7), py, 46])
            leaf.visual.material = mat_leaf
            scene.add_geometry(leaf, node_name=f"Leaf_B_{idx}_{leaf_angle}")

    output_path = "models/plant_gravitropism.glb"
    scene.export(output_path)
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    generate_clinostat()
    generate_arduino_bioreactor()
    generate_plant_gravitropism()
    print("ALL 3D MODELS SUCCESSFULLY GENERATED!")
