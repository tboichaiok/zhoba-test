import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the digital twin chamber building and loading logic
old_twin_logic_pattern = re.compile(
    r'function initDigitalTwinScene\(\)\s*\{.*?function animateTwinScene\(\)\s*\{.*?\}',
    re.DOTALL
)

new_twin_logic = """    // ==========================================
    // 5. 3D DIGITAL TWIN BIOREACTOR CHAMBER (WEBGL)
    // ==========================================
    let twinScene, twinCamera, twinRenderer, twinControls;
    let twinFanBlades, twinHeaterGlow, twinChamberModel;
    let twinPhytoPointLight, twinPhytoSpotLight;
    let twinWaterDrops, twinDropPositions, twinDropSpeeds;
    let twinWindParticles, twinWindPositions;
    let twinMaterialsWithWind = [];
    const TWIN_DROP_COUNT = 55;
    const TWIN_WIND_COUNT = 40;

    const twinState = {
      isFanActive: false,
      isPumpActive: false,
      isLedActive: true,
      isHeaterActive: false,
      soilMoisture: 48,
      temperature: 22.5,
      lightLux: 650
    };

    function attachPlantWindShader(material) {
      material.onBeforeCompile = (shader) => {
        shader.uniforms.uWindTime = { value: 0 };
        shader.uniforms.uWindIntensity = { value: 0 };

        shader.vertexShader = `
          uniform float uWindTime;
          uniform float uWindIntensity;
        ` + shader.vertexShader;

        shader.vertexShader = shader.vertexShader.replace(
          '#include <begin_vertex>',
          `
          #include <begin_vertex>
          // Plant foliage sway detection (leaves in front/center of chamber)
          if (position.z > -0.35 && position.y > -0.38) {
            float hFactor = clamp((position.y + 0.38) / 0.75, 0.0, 1.0);
            float swayX = sin(uWindTime * 14.0 + position.x * 8.0 + position.z * 6.0) * 0.045 * hFactor * uWindIntensity;
            float swayZ = cos(uWindTime * 11.0 + position.x * 6.0) * 0.03 * hFactor * uWindIntensity;
            transformed.x += swayX;
            transformed.z += swayZ;
            transformed.y += abs(swayX) * 0.15;
          }
          `
        );
        material.userData.windShader = shader;
        twinMaterialsWithWind.push(material);
      };
    }

    function initDigitalTwinScene() {
      const container = document.getElementById('twin-3d-canvas-container');
      if (!container) return;
      const w = container.clientWidth || 600;
      const h = container.clientHeight || 470;

      twinScene = new THREE.Scene();
      twinScene.background = new THREE.Color(0xF1F5F9);

      twinCamera = new THREE.PerspectiveCamera(40, w / h, 0.1, 100);
      twinCamera.position.set(0, 2.2, 4.4);

      twinRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
      twinRenderer.setSize(w, h);
      twinRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      twinRenderer.shadowMap.enabled = true;
      twinRenderer.shadowMap.type = THREE.PCFSoftShadowMap;
      twinRenderer.toneMapping = THREE.ACESFilmicToneMapping;
      twinRenderer.toneMappingExposure = 1.15;
      container.appendChild(twinRenderer.domElement);

      twinControls = new THREE.OrbitControls(twinCamera, twinRenderer.domElement);
      twinControls.enableDamping = true;
      twinControls.dampingFactor = 0.06;
      twinControls.autoRotate = false;
      twinControls.maxPolarAngle = Math.PI / 2 + 0.1;
      twinControls.minDistance = 1.8;
      twinControls.maxDistance = 8.0;

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 1.1);
      twinScene.add(ambientLight);

      const mainLight = new THREE.DirectionalLight(0xffffff, 1.4);
      mainLight.position.set(4, 8, 5);
      mainLight.castShadow = true;
      twinScene.add(mainLight);

      // Phyto Grow Lights (Overhead)
      twinPhytoPointLight = new THREE.PointLight(0xe040fb, 2.8, 6.0);
      twinPhytoPointLight.position.set(0, 1.4, 0.2);
      twinScene.add(twinPhytoPointLight);

      twinPhytoSpotLight = new THREE.SpotLight(0x7c3aed, 2.2, 5.5, Math.PI / 3, 0.4);
      twinPhytoSpotLight.position.set(0, 1.6, 0.2);
      twinPhytoSpotLight.target.position.set(0, -0.4, 0.2);
      twinScene.add(twinPhytoSpotLight);
      twinScene.add(twinPhytoSpotLight.target);

      // Studio Ground Floor Shadow Plate
      const floorPlane = new THREE.Mesh(
        new THREE.PlaneGeometry(12, 12),
        new THREE.ShadowMaterial({ opacity: 0.12 })
      );
      floorPlane.rotation.x = -Math.PI / 2;
      floorPlane.position.y = -1.0;
      floorPlane.receiveShadow = true;
      twinScene.add(floorPlane);

      const grid = new THREE.GridHelper(10, 16, 0xCBD5E1, 0xE2E8F0);
      grid.position.y = -1.01;
      twinScene.add(grid);

      // Load user's actual bioreactor_chamber.glb model!
      loadChamberModelIntoTwin();

      // Build interactive actuator attachments (water, fan blades, heater glow)
      buildTwinActuatorAttachments();

      window.addEventListener('resize', onTwinResize);
      setTimeout(onTwinResize, 200);
      animateTwinScene();
    }

    function loadChamberModelIntoTwin() {
      const loader = new THREE.GLTFLoader();
      loader.load(
        'models/bioreactor_chamber.glb',
        (gltf) => {
          twinChamberModel = gltf.scene;

          // Center and normalize scale
          const box = new THREE.Box3().setFromObject(twinChamberModel);
          const center = box.getCenter(new THREE.Vector3());
          const size = box.getSize(new THREE.Vector3());

          twinChamberModel.position.sub(center);

          const maxDim = Math.max(size.x, size.y, size.z);
          if (maxDim > 0) {
            const desiredSize = 2.9;
            const s = desiredSize / maxDim;
            twinChamberModel.scale.set(s, s, s);
          }

          twinChamberModel.traverse((node) => {
            if (node.isMesh) {
              node.castShadow = true;
              node.receiveShadow = true;
              if (node.material) {
                node.material.roughness = Math.max(0.18, node.material.roughness || 0.4);
                // Attach real wind-sway shader to plant leaves!
                attachPlantWindShader(node.material);
                node.material.needsUpdate = true;
              }
            }
          });

          twinScene.add(twinChamberModel);
        },
        undefined,
        (err) => {
          console.warn("Could not load models/bioreactor_chamber.glb, building procedural chamber", err);
          buildProceduralChamberInTwin();
        }
      );
    }

    function buildTwinActuatorAttachments() {
      const attachGroup = new THREE.Group();

      // 1. Spinning 3D Fan Unit & Airflow Generator (Left wall)
      const fanUnit = new THREE.Group();
      fanUnit.position.set(-1.18, 0.28, 0);

      // Housing
      const shroud = new THREE.Mesh(
        new THREE.BoxGeometry(0.1, 0.46, 0.46),
        new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5 })
      );
      fanUnit.add(shroud);

      // Blades rotor
      twinFanBlades = new THREE.Group();
      const hub = new THREE.Mesh(
        new THREE.CylinderGeometry(0.08, 0.08, 0.12, 16),
        new THREE.MeshStandardMaterial({ color: 0x0284c7, metalness: 0.5, roughness: 0.3 })
      );
      hub.rotation.z = Math.PI / 2;
      twinFanBlades.add(hub);

      const bladeMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, metalness: 0.4, roughness: 0.3 });
      for (let i = 0; i < 4; i++) {
        const blade = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.18, 0.03), bladeMat);
        blade.position.set(0, Math.sin(i * Math.PI / 2) * 0.12, Math.cos(i * Math.PI / 2) * 0.12);
        blade.rotation.x = i * Math.PI / 2 + 0.35;
        twinFanBlades.add(blade);
      }
      fanUnit.add(twinFanBlades);
      attachGroup.add(fanUnit);

      // Wind Flow Particles (Blowing across towards plants)
      const windGeo = new THREE.BufferGeometry();
      twinWindPositions = new Float32Array(TWIN_WIND_COUNT * 3);
      for (let i = 0; i < TWIN_WIND_COUNT; i++) {
        twinWindPositions[i * 3] = -1.1 + Math.random() * 1.8;
        twinWindPositions[i * 3 + 1] = 0.1 + (Math.random() - 0.5) * 0.4;
        twinWindPositions[i * 3 + 2] = (Math.random() - 0.5) * 0.6;
      }
      windGeo.setAttribute('position', new THREE.BufferAttribute(twinWindPositions, 3));
      twinWindParticles = new THREE.Points(
        windGeo,
        new THREE.PointsMaterial({ color: 0x0ea5e9, size: 0.045, transparent: true, opacity: 0.0 })
      );
      attachGroup.add(twinWindParticles);

      // 2. Water Droplets Particle System (Irrigation from nozzles into soil)
      const dropGeo = new THREE.BufferGeometry();
      twinDropPositions = new Float32Array(TWIN_DROP_COUNT * 3);
      twinDropSpeeds = new Float32Array(TWIN_DROP_COUNT);

      for (let i = 0; i < TWIN_DROP_COUNT; i++) {
        twinDropPositions[i * 3] = (Math.random() - 0.5) * 1.5;
        twinDropPositions[i * 3 + 1] = 0.4 - Math.random() * 0.8;
        twinDropPositions[i * 3 + 2] = -0.2 + (Math.random() - 0.5) * 0.8;
        twinDropSpeeds[i] = 0.025 + Math.random() * 0.035;
      }
      dropGeo.setAttribute('position', new THREE.BufferAttribute(twinDropPositions, 3));

      const dropMat = new THREE.PointsMaterial({
        color: 0x00e5ff,
        size: 0.065,
        transparent: true,
        opacity: 0.0
      });
      twinWaterDrops = new THREE.Points(dropGeo, dropMat);
      attachGroup.add(twinWaterDrops);

      // 3. PTC Ceramic Heater Thermal Glow Fixture (Right wall)
      const heaterBlock = new THREE.Group();
      heaterBlock.position.set(1.18, 0.28, 0);

      const hMount = new THREE.Mesh(
        new THREE.BoxGeometry(0.1, 0.38, 0.38),
        new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.5 })
      );
      heaterBlock.add(hMount);

      twinHeaterGlow = new THREE.Mesh(
        new THREE.BoxGeometry(0.12, 0.3, 0.3),
        new THREE.MeshStandardMaterial({
          color: 0x94a3b8,
          emissive: 0xff3b00,
          emissiveIntensity: 0.0,
          roughness: 0.3
        })
      );
      heaterBlock.add(twinHeaterGlow);
      attachGroup.add(heaterBlock);

      twinScene.add(attachGroup);
    }

    function buildProceduralChamberInTwin() {
      const group = new THREE.Group();
      const acrylicMat = new THREE.MeshPhysicalMaterial({ color: 0xe0f2fe, transparent: true, opacity: 0.4, roughness: 0.1 });
      const box = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.8, 1.8), acrylicMat);
      group.add(box);
      twinScene.add(group);
    }

    function resetTwinCamera() {
      twinCamera.position.set(0, 2.2, 4.4);
      twinControls.target.set(0, 0, 0);
      twinControls.update();
    }

    function onTwinResize() {
      const container = document.getElementById('twin-3d-canvas-container');
      if (!container || !twinRenderer) return;
      const w = container.clientWidth || 600;
      const h = container.clientHeight || 470;
      twinCamera.aspect = w / h;
      twinCamera.updateProjectionMatrix();
      twinRenderer.setSize(w, h);
    }

    // Dynamic Actuator State Updater (Called on scenarios, sliders, or test buttons!)
    function updateDigitalTwinActuators(state) {
      if (state.pump !== undefined) twinState.isPumpActive = state.pump;
      if (state.led !== undefined) twinState.isLedActive = state.led;
      if (state.heater !== undefined) twinState.isHeaterActive = state.heater;
      if (state.fan !== undefined) twinState.isFanActive = state.fan;
      if (state.soil !== undefined) twinState.soilMoisture = state.soil;
      if (state.temp !== undefined) twinState.temperature = state.temp;
      if (state.light !== undefined) twinState.lightLux = state.light;

      // 1. Phyto Lighting Intensity & Color
      if (twinPhytoPointLight) {
        twinPhytoPointLight.intensity = twinState.isLedActive ? 2.8 : 0.08;
      }
      if (twinPhytoSpotLight) {
        twinPhytoSpotLight.intensity = twinState.isLedActive ? 2.2 : 0.05;
      }

      // 2. Water Droplets Opacity
      if (twinWaterDrops) {
        twinWaterDrops.material.opacity = twinState.isPumpActive ? 0.95 : 0.0;
      }

      // 3. Wind Flow Particle Ribbon Opacity
      if (twinWindParticles) {
        twinWindParticles.material.opacity = twinState.isFanActive ? 0.75 : 0.0;
      }

      // 4. Update Floating Status Chips
      updateTwinHUDChip('fan', twinState.isFanActive, 'ЖЕЛДЕТУ ON (2400 RPM)', 'ӨШІРУЛІ', 'rose');
      updateTwinHUDChip('pump', twinState.isPumpActive, 'СУАРУДА (3-6В)', 'ӨШІРУЛІ', 'cyan');
      updateTwinHUDChip('led', twinState.isLedActive, 'ҚОСУЛЫ (660nm)', 'ӨШІРУЛІ', 'purple');
      updateTwinHUDChip('heater', twinState.isHeaterActive, 'ЖЫЛЫТУДА (PTC)', 'ӨШІРУЛІ', 'amber');
    }

    function updateTwinHUDChip(name, active, onText, offText, color) {
      const dot = document.getElementById(`twin-dot-${name}`);
      const txt = document.getElementById(`twin-txt-${name}`);
      const tag = document.getElementById(`twin-tag-${name}`);

      if (dot && txt && tag) {
        if (active) {
          dot.className = `w-2 h-2 rounded-full bg-tech-${color} shadow-sm shadow-tech-${color}/50 animate-ping`;
          txt.innerText = onText;
          tag.className = `px-2.5 py-1 rounded-lg bg-${color}-50/95 border border-${color}-300 text-${color}-800 shadow-sm flex items-center gap-1.5 transition-all`;
        } else {
          dot.className = "w-2 h-2 rounded-full bg-slate-400";
          txt.innerText = offText;
          tag.className = "px-2.5 py-1 rounded-lg bg-white/90 border border-slate-200 text-lab-700 shadow-sm flex items-center gap-1.5 transition-all";
        }
      }
    }

    function animateTwinScene() {
      requestAnimationFrame(animateTwinScene);

      // 1. Fan Rotation (High speed when fan is active, gentle idle when off)
      if (twinFanBlades) {
        const fanSpeed = twinState.isFanActive ? 0.42 : 0.003;
        twinFanBlades.rotation.x += fanSpeed;
      }

      // 2. Wind Flow Particle Animation across the chamber
      if (twinWindParticles && twinState.isFanActive) {
        const pos = twinWindParticles.geometry.attributes.position.array;
        for (let i = 0; i < TWIN_WIND_COUNT; i++) {
          pos[i * 3] += 0.035; // moves from left to right across plants
          if (pos[i * 3] > 0.8) {
            pos[i * 3] = -1.1;
          }
        }
        twinWindParticles.geometry.attributes.position.needsUpdate = true;
      }

      // 3. Plant Leaves Wind Sway (Vegetation rustles & sways in airflow!)
      twinMaterialsWithWind.forEach((mat) => {
        if (mat.userData.windShader) {
          mat.userData.windShader.uniforms.uWindTime.value += 0.05;
          const targetIntensity = twinState.isFanActive ? 1.0 : 0.0;
          const cur = mat.userData.windShader.uniforms.uWindIntensity.value;
          mat.userData.windShader.uniforms.uWindIntensity.value += (targetIntensity - cur) * 0.08;
        }
      });

      // 4. Heater Thermal Glow Animation
      if (twinHeaterGlow) {
        if (twinState.isHeaterActive) {
          const pulse = 1.3 + Math.sin(Date.now() * 0.007) * 0.5;
          twinHeaterGlow.material.emissiveIntensity = pulse;
          twinHeaterGlow.material.color.setHex(0xd97706);
        } else {
          twinHeaterGlow.material.emissiveIntensity = 0.0;
          twinHeaterGlow.material.color.setHex(0x94a3b8);
        }
      }

      // 5. Falling Water Droplets Animation
      if (twinWaterDrops && twinState.isPumpActive) {
        const positions = twinWaterDrops.geometry.attributes.position.array;
        for (let i = 0; i < TWIN_DROP_COUNT; i++) {
          positions[i * 3 + 1] -= twinDropSpeeds[i];
          if (positions[i * 3 + 1] < -0.65) {
            positions[i * 3 + 1] = 0.4;
          }
        }
        twinWaterDrops.geometry.attributes.position.needsUpdate = true;
      }

      twinControls.update();
      twinRenderer.render(twinScene, twinCamera);
    }"""

if old_twin_logic_pattern.search(html):
    html = old_twin_logic_pattern.sub(new_twin_logic, html)
    print("Replaced twin logic with new chamber and plant-sway shader!")
else:
    print("Warning: old_twin_logic_pattern not found directly, looking for fallback...")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html successfully!")
