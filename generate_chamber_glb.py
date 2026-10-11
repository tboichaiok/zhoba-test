import os
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

def create_pbr(color_rgba, metallic=0.2, roughness=0.5):
    return PBRMaterial(
        baseColorFactor=color_rgba,
        metallicFactor=float(metallic),
        roughnessFactor=float(roughness)
    )

def generate_chamber():
    print("Generating Complete Bioreactor Chamber 3D Model...")
    scene = trimesh.Scene()

    # Materials
    mat_white_chassis = create_pbr([0.94, 0.95, 0.96, 1.0], metallic=0.1, roughness=0.3)
    mat_metal_frame = create_pbr([0.75, 0.78, 0.82, 1.0], metallic=0.9, roughness=0.15)
    mat_acrylic = create_pbr([0.85, 0.95, 1.0, 0.45], metallic=0.1, roughness=0.05)
    mat_soil = create_pbr([0.25, 0.18, 0.12, 1.0], metallic=0.0, roughness=0.9)
    mat_plant = create_pbr([0.15, 0.85, 0.25, 1.0], metallic=0.1, roughness=0.4)
    mat_fan_housing = create_pbr([0.15, 0.16, 0.18, 1.0], metallic=0.3, roughness=0.5)
    mat_fan_rotor = create_pbr([0.1, 0.5, 0.85, 1.0], metallic=0.4, roughness=0.3) # Cyan rotor
    mat_heater_cold = create_pbr([0.8, 0.3, 0.1, 1.0], metallic=0.6, roughness=0.3) # PTC heater
    mat_phyto_bar = create_pbr([0.9, 0.1, 0.8, 1.0], metallic=0.3, roughness=0.2) # Phyto LED
    mat_tube = create_pbr([0.3, 0.75, 0.9, 0.7], metallic=0.1, roughness=0.2) # Silicone tube
    mat_sensor = create_pbr([0.96, 0.96, 0.98, 1.0], metallic=0.1, roughness=0.3) # DHT22

    # 1. Base Platform & Service Deck
    base = trimesh.creation.box([220, 180, 10])
    base.apply_translation([0, 0, 5])
    base.visual.material = mat_white_chassis
    scene.add_geometry(base, node_name="Lab_Base_Plate")

    # Anti-slip rubber feet
    for dx in [-90, 90]:
        for dy in [-75, 75]:
            foot = trimesh.creation.cylinder(radius=8, height=6)
            foot.apply_translation([dx, dy, -3])
            foot.visual.material = create_pbr([0.1, 0.1, 0.1, 1.0], metallic=0.2, roughness=0.8)
            scene.add_geometry(foot, node_name=f"Rubber_Foot_{dx}_{dy}")

    # 2. Transparent Chamber Walls (Open front / cutaway laboratory view)
    # Back wall
    back_wall = trimesh.creation.box([160, 6, 120])
    back_wall.apply_translation([0, 60, 70])
    back_wall.visual.material = mat_acrylic
    scene.add_geometry(back_wall, node_name="Acrylic_Back_Wall")

    # Left wall (with exhaust port)
    left_wall = trimesh.creation.box([6, 120, 120])
    left_wall.apply_translation([-80, 0, 70])
    left_wall.visual.material = mat_acrylic
    scene.add_geometry(left_wall, node_name="Acrylic_Left_Wall")

    # Right wall (with intake port)
    right_wall = trimesh.creation.box([6, 120, 120])
    right_wall.apply_translation([80, 0, 70])
    right_wall.visual.material = mat_acrylic
    scene.add_geometry(right_wall, node_name="Acrylic_Right_Wall")

    # Top ceiling
    ceiling = trimesh.creation.box([166, 126, 6])
    ceiling.apply_translation([0, 0, 130])
    ceiling.visual.material = mat_metal_frame
    scene.add_geometry(ceiling, node_name="Chamber_Ceiling")

    # Corner aluminum framing posts
    for cx in [-80, 80]:
        for cy in [-60, 60]:
            post = trimesh.creation.box([8, 8, 120])
            post.apply_translation([cx, cy, 70])
            post.visual.material = mat_metal_frame
            scene.add_geometry(post, node_name=f"Frame_Post_{cx}_{cy}")

    # 3. Growth Tray & Soil Bed
    tray = trimesh.creation.box([140, 100, 20])
    tray.apply_translation([0, 0, 20])
    tray.visual.material = mat_white_chassis
    scene.add_geometry(tray, node_name="Substrate_Tray")

    soil = trimesh.creation.box([134, 94, 16])
    soil.apply_translation([0, 0, 22])
    soil.visual.material = mat_soil
    scene.add_geometry(soil, node_name="Soil_Substrate_Bed")

    # Radish Sprouts inside tray
    for sx in np.linspace(-45, 45, 5):
        for sy in np.linspace(-30, 30, 3):
            stem = trimesh.creation.cylinder(radius=1.2, height=18)
            stem.apply_translation([sx, sy, 38])
            stem.visual.material = mat_plant
            scene.add_geometry(stem, node_name=f"Sprout_Stem_{sx}_{sy}")

            leaf1 = trimesh.creation.box([10, 6, 1.2])
            leaf1.apply_translation([sx + 5, sy, 46])
            leaf1.visual.material = mat_plant
            scene.add_geometry(leaf1, node_name=f"Leaf1_{sx}_{sy}")

            leaf2 = trimesh.creation.box([10, 6, 1.2])
            leaf2.apply_translation([sx - 5, sy, 46])
            leaf2.visual.material = mat_plant
            scene.add_geometry(leaf2, node_name=f"Leaf2_{sx}_{sy}")

    # 4. Actuator 1: DC Cooling Fan (40mm) mounted on left wall
    fan_box = trimesh.creation.box([14, 42, 42])
    fan_box.apply_translation([-80, 0, 95])
    fan_box.visual.material = mat_fan_housing
    scene.add_geometry(fan_box, node_name="Fan_Shroud_Housing")

    fan_hub = trimesh.creation.cylinder(radius=10, height=16)
    fan_hub.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    fan_hub.apply_translation([-80, 0, 95])
    fan_hub.visual.material = mat_fan_rotor
    scene.add_geometry(fan_hub, node_name="Fan_Center_Rotor_Hub")

    # Fan Blades (4 blades)
    for b_angle in [0, np.pi/2, np.pi, np.pi*1.5]:
        blade = trimesh.creation.box([12, 14, 2.5])
        blade.apply_transform(trimesh.transformations.rotation_matrix(b_angle, [1, 0, 0]))
        blade.apply_translation([-80, np.sin(b_angle)*12, 95 + np.cos(b_angle)*12])
        blade.visual.material = mat_fan_rotor
        scene.add_geometry(blade, node_name=f"Fan_Blade_{b_angle}")

    # 5. Actuator 2: PTC Ceramic Heater Block mounted on right wall
    heater_base = trimesh.creation.box([14, 32, 32])
    heater_base.apply_translation([80, 0, 95])
    heater_base.visual.material = mat_heater_cold
    scene.add_geometry(heater_base, node_name="PTC_Ceramic_Heater_Block")

    # Heater thermal fins
    for fin_y in np.linspace(-12, 12, 5):
        fin = trimesh.creation.box([18, 2, 28])
        fin.apply_translation([80, fin_y, 95])
        fin.visual.material = create_pbr([0.9, 0.4, 0.2, 1.0], metallic=0.7, roughness=0.3)
        scene.add_geometry(fin, node_name=f"Heater_Fin_{fin_y}")

    # 6. Actuator 3: Overhead Phyto-LED Fixture (Ceiling mounted)
    phyto_rack = trimesh.creation.box([130, 40, 8])
    phyto_rack.apply_translation([0, 0, 124])
    phyto_rack.visual.material = mat_metal_frame
    scene.add_geometry(phyto_rack, node_name="Phyto_LED_Fixture_Body")

    # Red & Blue LED Strips
    led_strip1 = trimesh.creation.box([120, 8, 3])
    led_strip1.apply_translation([0, -10, 119])
    led_strip1.visual.material = mat_phyto_bar
    scene.add_geometry(led_strip1, node_name="LED_Strip_Magenta")

    led_strip2 = trimesh.creation.box([120, 8, 3])
    led_strip2.apply_translation([0, 10, 119])
    led_strip2.visual.material = create_pbr([0.1, 0.3, 0.95, 1.0], metallic=0.3, roughness=0.2) # Royal blue
    scene.add_geometry(led_strip2, node_name="LED_Strip_Blue")

    # 7. Actuator 4: Irrigation System (Water Pump & Manifold)
    pump = trimesh.creation.cylinder(radius=10, height=26)
    pump.apply_translation([-95, -60, 20])
    pump.visual.material = create_pbr([0.2, 0.2, 0.25, 1.0], metallic=0.4, roughness=0.4)
    scene.add_geometry(pump, node_name="Submersible_Water_Pump")

    # Water delivery pipe along back wall
    pipe = trimesh.creation.cylinder(radius=3, height=130)
    pipe.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    pipe.apply_translation([0, 52, 45])
    pipe.visual.material = mat_tube
    scene.add_geometry(pipe, node_name="Irrigation_Supply_Manifold")

    # 4 Drip nozzles pointed at soil
    for nx in [-45, -15, 15, 45]:
        nozzle = trimesh.creation.cylinder(radius=1.8, height=12)
        nozzle.apply_translation([nx, 52, 38])
        nozzle.visual.material = create_pbr([0.9, 0.75, 0.2, 1.0], metallic=0.8, roughness=0.2) # Brass
        scene.add_geometry(nozzle, node_name=f"Drip_Nozzle_{nx}")

    # 8. Sensor 1: DHT22 Sensor on Back Wall
    dht_body = trimesh.creation.box([14, 8, 20])
    dht_body.apply_translation([0, 56, 95])
    dht_body.visual.material = mat_sensor
    scene.add_geometry(dht_body, node_name="DHT22_Chamber_Probe")

    # 9. Sensor 2: Capacitive Soil Moisture Probe
    soil_probe = trimesh.creation.box([12, 3, 35])
    soil_probe.apply_translation([48, -25, 30])
    soil_probe.visual.material = create_pbr([0.08, 0.08, 0.1, 1.0], metallic=0.3, roughness=0.5)
    scene.add_geometry(soil_probe, node_name="Capacitive_Soil_Moisture_Probe")

    # 10. Sensor 3: Photocell LDR
    ldr = trimesh.creation.cylinder(radius=4, height=4)
    ldr.apply_translation([-48, -25, 32])
    ldr.visual.material = create_pbr([0.8, 0.2, 0.2, 1.0], metallic=0.5, roughness=0.3)
    scene.add_geometry(ldr, node_name="LDR_Light_Sensor_Head")

    output_path = "models/bioreactor_chamber.glb"
    scene.export(output_path)
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    generate_chamber()
