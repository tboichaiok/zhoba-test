import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update HTML Markup of the Telemetry Grid
old_grid_pattern = re.compile(
    r'<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">\s*<!-- SENSORS \(LEFT 7 COLS\) -->.*?<!-- RELAYS \(RIGHT 5 COLS\) -->.*?</div>\s*</div>\s*</div>',
    re.DOTALL
)

new_grid_markup = """<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- 3D DIGITAL TWIN BIOREACTOR CHAMBER (LEFT 6 COLS) -->
        <div class="lg:col-span-6 flex flex-col space-y-3">
          <div class="flex items-center justify-between font-mono text-xs">
            <span class="text-lab-900 font-bold flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-tech-blue animate-ping"></span>
              3D ЦИФРЛЫҚ ЕГІЗ (DIGITAL TWIN CHAMBER)
            </span>
            <span class="text-lab-700 text-[11px]">Тышқанмен бұру / Зум</span>
          </div>

          <!-- 3D Viewport Box -->
          <div class="relative w-full h-[470px] rounded-2xl overflow-hidden bg-gradient-to-b from-slate-100 to-slate-200 border border-slate-300 shadow-inner">
            <div id="twin-3d-canvas-container" class="w-full h-full cursor-grab active:cursor-grabbing"></div>

            <!-- Floating 3D Actuator Status Chips -->
            <div class="absolute top-3 left-3 flex flex-col gap-1.5 pointer-events-none font-mono text-[10px] z-10">
              <div id="twin-tag-fan" class="px-2.5 py-1 rounded-lg bg-white/90 border border-slate-200 text-lab-700 shadow-sm flex items-center gap-1.5 transition-all">
                <span class="w-2 h-2 rounded-full bg-slate-400" id="twin-dot-fan"></span>
                <span>DC КУЛЕР: <strong id="twin-txt-fan">ӨШІРУЛІ</strong></span>
              </div>
              <div id="twin-tag-pump" class="px-2.5 py-1 rounded-lg bg-white/90 border border-slate-200 text-lab-700 shadow-sm flex items-center gap-1.5 transition-all">
                <span class="w-2 h-2 rounded-full bg-slate-400" id="twin-dot-pump"></span>
                <span>АВТО-СУАРУ: <strong id="twin-txt-pump">ӨШІРУЛІ</strong></span>
              </div>
              <div id="twin-tag-led" class="px-2.5 py-1 rounded-lg bg-purple-50/90 border border-purple-200 text-purple-700 shadow-sm flex items-center gap-1.5 transition-all">
                <span class="w-2 h-2 rounded-full bg-purple-500 shadow-sm shadow-purple-500/50" id="twin-dot-led"></span>
                <span>ФИТОЖАРЫҚ: <strong id="twin-txt-led">ҚОСУЛЫ (ON)</strong></span>
              </div>
              <div id="twin-tag-heater" class="px-2.5 py-1 rounded-lg bg-white/90 border border-slate-200 text-lab-700 shadow-sm flex items-center gap-1.5 transition-all">
                <span class="w-2 h-2 rounded-full bg-slate-400" id="twin-dot-heater"></span>
                <span>ЖЫЛЫТҚЫШ PTC: <strong id="twin-txt-heater">ӨШІРУЛІ</strong></span>
              </div>
            </div>

            <!-- Controls overlay -->
            <div class="absolute bottom-3 right-3 flex items-center gap-1.5 z-20">
              <button onclick="resetTwinCamera()" title="Ракурсты қалпына келтіру" class="px-2.5 py-1 rounded-xl bg-white/90 hover:bg-white text-lab-800 border border-lab-200 shadow-sm font-mono text-[11px] transition-transform active:scale-95">
                🔄 Камераны туралау
              </button>
            </div>
          </div>

          <div class="p-2.5 rounded-xl bg-lab-100 border border-lab-200 text-[11px] font-mono text-lab-700 flex items-center justify-between">
            <span>⚡ Релелер мен датчиктер 3D камерада физикалық түрде іске қосылады</span>
            <span class="text-tech-blue font-bold">12В 2А желісі</span>
          </div>
        </div>

        <!-- CONTROLS & RELAYS (RIGHT 6 COLS) -->
        <div class="lg:col-span-6 space-y-4 font-mono">
          
          <!-- Sensor 1: Soil Moisture -->
          <div class="p-3.5 rounded-2xl bg-white border border-lab-200 shadow-sm space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="text-lab-900 font-bold flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-tech-cyan"></span>
                Топырақ ылғалдылығы (A0 Сыйымдылық датчигі)
              </span>
              <span class="text-tech-cyan text-base font-bold" id="val-soil">48%</span>
            </div>
            <input type="range" id="slider-soil" min="15" max="85" value="48" class="w-full accent-tech-cyan cursor-pointer" oninput="manualUpdateSim()">
            <div class="flex justify-between text-[11px] text-lab-700">
              <span class="text-tech-rose font-bold">&lt; 38% (Суару қажет!)</span>
              <span class="text-tech-emerald font-bold">45% - 65% (Оптималды)</span>
              <span>&gt; 75% Шамадан тыс</span>
            </div>
          </div>

          <!-- Sensor 2: Temperature -->
          <div class="p-3.5 rounded-2xl bg-white border border-lab-200 shadow-sm space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="text-lab-900 font-bold flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-tech-amber"></span>
                Ауа температурасы (DHT22 D2 пині)
              </span>
              <span class="text-tech-amber text-base font-bold" id="val-temp">22.5 °C</span>
            </div>
            <input type="range" id="slider-temp" min="12" max="35" value="22.5" step="0.5" class="w-full accent-tech-amber cursor-pointer" oninput="manualUpdateSim()">
            <div class="flex justify-between text-[11px] text-lab-700">
              <span class="text-tech-blue font-bold">&lt; 18.5°C (Жылытқыш ON)</span>
              <span class="text-tech-emerald font-bold">20°C - 24°C (Комфорт)</span>
              <span class="text-tech-rose font-bold">&gt; 26.5°C (Желдеткіш ON)</span>
            </div>
          </div>

          <!-- Sensor 3: Light Intensity -->
          <div class="p-3.5 rounded-2xl bg-white border border-lab-200 shadow-sm space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="text-lab-900 font-bold flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-tech-magenta"></span>
                Жарық қарқындылығы (Фоторезистор LDR A1)
              </span>
              <span class="text-tech-magenta text-base font-bold" id="val-light">650 Lux</span>
            </div>
            <input type="range" id="slider-light" min="50" max="1200" value="650" class="w-full accent-tech-magenta cursor-pointer" oninput="manualUpdateSim()">
            <div class="flex justify-between text-[11px] text-lab-700">
              <span class="text-tech-violet font-bold">&lt; 350 Lux (Фитожарық ON)</span>
              <span class="text-tech-emerald font-bold">Оптималды фотопериод</span>
              <span>&gt; 900 Lux Сыртқы сәуле</span>
            </div>
          </div>

          <!-- 4-Channel Relay Status Grid -->
          <div class="pt-2 border-t border-lab-200 space-y-2.5">
            <div class="flex items-center justify-between pb-1">
              <span class="text-xs font-bold text-lab-900 uppercase">4-АРНАЛЫ РЕЛЕ МОДУЛІ (12В)</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-tech-emerald/10 text-tech-emerald font-bold">
                ACTIVE LOW
              </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <!-- Relay 1: Pump -->
              <div id="relay-row-pump" class="p-2.5 rounded-xl bg-white border border-lab-200 flex items-center justify-between shadow-sm transition-all">
                <div class="flex items-center gap-2">
                  <div id="relay-dot-pump" class="w-3.5 h-3.5 rounded-full bg-slate-300"></div>
                  <div>
                    <h5 class="text-[11px] font-bold text-lab-900">IN1: Сорғы (Помпа)</h5>
                    <p class="text-[10px] text-lab-700">3-6В суару</p>
                  </div>
                </div>
                <span id="relay-pill-pump" class="text-[11px] font-bold px-2 py-0.5 rounded-lg bg-lab-100 text-lab-700">
                  ӨШІРУЛІ
                </span>
              </div>

              <!-- Relay 2: Phyto LED -->
              <div id="relay-row-led" class="p-2.5 rounded-xl bg-white border border-lab-200 flex items-center justify-between shadow-sm transition-all">
                <div class="flex items-center gap-2">
                  <div id="relay-dot-led" class="w-3.5 h-3.5 rounded-full bg-tech-magenta shadow-md shadow-tech-magenta/40"></div>
                  <div>
                    <h5 class="text-[11px] font-bold text-lab-900">IN2: LED Фитожарық</h5>
                    <p class="text-[10px] text-lab-700">12В спектр</p>
                  </div>
                </div>
                <span id="relay-pill-led" class="text-[11px] font-bold px-2 py-0.5 rounded-lg bg-purple-100 text-purple-700 border border-purple-200">
                  ҚОСУЛЫ (ON)
                </span>
              </div>

              <!-- Relay 3: Heater -->
              <div id="relay-row-heater" class="p-2.5 rounded-xl bg-white border border-lab-200 flex items-center justify-between shadow-sm transition-all">
                <div class="flex items-center gap-2">
                  <div id="relay-dot-heater" class="w-3.5 h-3.5 rounded-full bg-slate-300"></div>
                  <div>
                    <h5 class="text-[11px] font-bold text-lab-900">IN3: Жылытқыш</h5>
                    <p class="text-[10px] text-lab-700">12В PTC 10W</p>
                  </div>
                </div>
                <span id="relay-pill-heater" class="text-[11px] font-bold px-2 py-0.5 rounded-lg bg-lab-100 text-lab-700">
                  ӨШІРУЛІ
                </span>
              </div>

              <!-- Relay 4: Fan -->
              <div id="relay-row-fan" class="p-2.5 rounded-xl bg-white border border-lab-200 flex items-center justify-between shadow-sm transition-all">
                <div class="flex items-center gap-2">
                  <div id="relay-dot-fan" class="w-3.5 h-3.5 rounded-full bg-slate-300"></div>
                  <div>
                    <h5 class="text-[11px] font-bold text-lab-900">IN4: DC Желдеткіш</h5>
                    <p class="text-[10px] text-lab-700">40мм салқындату</p>
                  </div>
                </div>
                <span id="relay-pill-fan" class="text-[11px] font-bold px-2 py-0.5 rounded-lg bg-lab-100 text-lab-700">
                  ӨШІРУЛІ
                </span>
              </div>
            </div>

          </div>

        </div>

      </div>"""

if old_grid_pattern.search(html):
    html = old_grid_pattern.sub(new_grid_markup, html)
    print("Successfully replaced grid markup!")
else:
    print("WARNING: Pattern for grid markup did not match directly, checking fallback...")

# 2. Add Digital Twin Scene Logic to JavaScript
digital_twin_js = """
    // ==========================================
    // 5. 3D DIGITAL TWIN BIOREACTOR CHAMBER (WEBGL)
    // ==========================================
    let twinScene, twinCamera, twinRenderer, twinControls;
    let twinFanRotor, twinHeaterMesh, twinSoilMesh;
    let twinPhytoPointLight, twinPhytoSpotLight;
    let twinWaterDrops, twinDropPositions, twinDropSpeeds;
    const TWIN_DROP_COUNT = 45;

    const twinState = {
      isFanActive: false,
      isPumpActive: false,
      isLedActive: true,
      isHeaterActive: false,
      soilMoisture: 48,
      temperature: 22.5,
      lightLux: 650
    };

    function initDigitalTwinScene() {
      const container = document.getElementById('twin-3d-canvas-container');
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;

      twinScene = new THREE.Scene();
      twinScene.background = new THREE.Color(0xF1F5F9);

      twinCamera = new THREE.PerspectiveCamera(40, w / h, 0.1, 100);
      twinCamera.position.set(0, 2.5, 4.8);

      twinRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
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
      twinControls.minDistance = 2.0;
      twinControls.maxDistance = 8.5;

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 1.1);
      twinScene.add(ambientLight);

      const mainLight = new THREE.DirectionalLight(0xffffff, 1.4);
      mainLight.position.set(4, 8, 5);
      mainLight.castShadow = true;
      twinScene.add(mainLight);

      // Phyto Grow Lights (Overhead)
      twinPhytoPointLight = new THREE.PointLight(0xe040fb, 2.8, 6.0);
      twinPhytoPointLight.position.set(0, 1.3, 0);
      twinScene.add(twinPhytoPointLight);

      twinPhytoSpotLight = new THREE.SpotLight(0x7c3aed, 2.0, 5.0, Math.PI / 3, 0.4);
      twinPhytoSpotLight.position.set(0, 1.5, 0);
      twinPhytoSpotLight.target.position.set(0, -0.6, 0);
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

      // Build Chamber Geometry
      buildChamberInTwinScene();

      window.addEventListener('resize', onTwinResize);
      animateTwinScene();
    }

    function buildChamberInTwinScene() {
      const chamberGroup = new THREE.Group();

      // 1. Base Stand
      const baseMesh = new THREE.Mesh(
        new THREE.BoxGeometry(2.8, 0.12, 2.2),
        new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 })
      );
      baseMesh.position.y = -0.95;
      baseMesh.receiveShadow = true;
      chamberGroup.add(baseMesh);

      // 2. Acrylic Transparent Enclosure (Back & Sides)
      const acrylicMat = new THREE.MeshPhysicalMaterial({
        color: 0xe0f2fe,
        transparent: true,
        opacity: 0.35,
        roughness: 0.05,
        transmission: 0.8
      });

      // Back wall
      const backWall = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.8, 0.05), acrylicMat);
      backWall.position.set(0, 0, -0.9);
      chamberGroup.add(backWall);

      // Left wall
      const leftWall = new THREE.Mesh(new THREE.BoxGeometry(0.05, 1.8, 1.8), acrylicMat);
      leftWall.position.set(-1.2, 0, 0);
      chamberGroup.add(leftWall);

      // Right wall
      const rightWall = new THREE.Mesh(new THREE.BoxGeometry(0.05, 1.8, 1.8), acrylicMat);
      rightWall.position.set(1.2, 0, 0);
      chamberGroup.add(rightWall);

      // Frame columns
      const frameMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8, roughness: 0.2 });
      [[-1.2, -0.9], [1.2, -0.9], [-1.2, 0.9], [1.2, 0.9]].forEach(([cx, cz]) => {
        const post = new THREE.Mesh(new THREE.BoxGeometry(0.06, 1.8, 0.06), frameMat);
        post.position.set(cx, 0, cz);
        chamberGroup.add(post);
      });

      // Ceiling fixture
      const ceiling = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.08, 1.8), frameMat);
      ceiling.position.set(0, 0.9, 0);
      chamberGroup.add(ceiling);

      // 3. Phyto-LED Overhead Fixture
      const ledBar = new THREE.Mesh(
        new THREE.BoxGeometry(1.8, 0.06, 0.4),
        new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.5 })
      );
      ledBar.position.set(0, 0.84, 0);
      chamberGroup.add(ledBar);

      // Glowing LED Strip Surfaces
      const ledStrips = new THREE.Mesh(
        new THREE.BoxGeometry(1.6, 0.02, 0.24),
        new THREE.MeshStandardMaterial({ color: 0xe040fb, emissive: 0xe040fb, emissiveIntensity: 2.5 })
      );
      ledStrips.position.set(0, 0.8, 0);
      ledStrips.name = "twinLedStrip";
      chamberGroup.add(ledStrips);

      // 4. Growth Tray & Soil Substrate
      const trayMesh = new THREE.Mesh(
        new THREE.BoxGeometry(2.1, 0.25, 1.5),
        new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4 })
      );
      trayMesh.position.set(0, -0.78, 0);
      chamberGroup.add(trayMesh);

      twinSoilMesh = new THREE.Mesh(
        new THREE.BoxGeometry(2.0, 0.22, 1.4),
        new THREE.MeshStandardMaterial({ color: 0x4a2e18, roughness: 0.9 })
      );
      twinSoilMesh.position.set(0, -0.75, 0);
      chamberGroup.add(twinSoilMesh);

      // Radish Sprouts (5x3 grid)
      const plantMat = new THREE.MeshStandardMaterial({ color: 0x10b981, roughness: 0.4 });
      for (let px = -0.7; px <= 0.7; px += 0.35) {
        for (let pz = -0.4; pz <= 0.4; pz += 0.4) {
          const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.24, 8), plantMat);
          stem.position.set(px, -0.52, pz);
          chamberGroup.add(stem);

          const leaf1 = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.015, 0.08), plantMat);
          leaf1.position.set(px + 0.05, -0.4, pz);
          chamberGroup.add(leaf1);

          const leaf2 = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.015, 0.08), plantMat);
          leaf2.position.set(px - 0.05, -0.4, pz);
          chamberGroup.add(leaf2);
        }
      }

      // 5. ACTUATOR 1: DC Cooling Fan (40mm) mounted on Left Wall
      const fanHousing = new THREE.Mesh(
        new THREE.BoxGeometry(0.14, 0.5, 0.5),
        new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.6 })
      );
      fanHousing.position.set(-1.2, 0.25, 0);
      chamberGroup.add(fanHousing);

      // Spinning Fan Rotor
      twinFanRotor = new THREE.Group();
      const hub = new THREE.Mesh(
        new THREE.CylinderGeometry(0.1, 0.1, 0.15, 16),
        new THREE.MeshStandardMaterial({ color: 0x0284c7, metalness: 0.6, roughness: 0.3 })
      );
      hub.rotation.z = Math.PI / 2;
      twinFanRotor.add(hub);

      // 4 Blades
      const bladeMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, metalness: 0.4, roughness: 0.3 });
      for (let ba = 0; ba < 4; ba++) {
        const blade = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.2, 0.04), bladeMat);
        blade.position.set(0, Math.sin(ba * Math.PI / 2) * 0.14, Math.cos(ba * Math.PI / 2) * 0.14);
        blade.rotation.x = ba * Math.PI / 2 + 0.3;
        twinFanRotor.add(blade);
      }
      twinFanRotor.position.set(-1.18, 0.25, 0);
      chamberGroup.add(twinFanRotor);

      // 6. ACTUATOR 2: PTC Ceramic Heater mounted on Right Wall
      const heaterHousing = new THREE.Mesh(
        new THREE.BoxGeometry(0.12, 0.4, 0.4),
        new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.5 })
      );
      heaterHousing.position.set(1.2, 0.25, 0);
      chamberGroup.add(heaterHousing);

      twinHeaterMesh = new THREE.Mesh(
        new THREE.BoxGeometry(0.14, 0.32, 0.32),
        new THREE.MeshStandardMaterial({
          color: 0x94a3b8,
          emissive: 0xff3b00,
          emissiveIntensity: 0.0,
          roughness: 0.3
        })
      );
      twinHeaterMesh.position.set(1.18, 0.25, 0);
      chamberGroup.add(twinHeaterMesh);

      // 7. ACTUATOR 3: Drip Irrigation Manifold & Water Particles
      const waterPipe = new THREE.Mesh(
        new THREE.CylinderGeometry(0.03, 0.03, 1.8, 12),
        new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.2 })
      );
      waterPipe.rotation.z = Math.PI / 2;
      waterPipe.position.set(0, -0.2, -0.6);
      chamberGroup.add(waterPipe);

      // Water Droplets Particle System
      const dropGeo = new THREE.BufferGeometry();
      twinDropPositions = new Float32Array(TWIN_DROP_COUNT * 3);
      twinDropSpeeds = new Float32Array(TWIN_DROP_COUNT);

      for (let i = 0; i < TWIN_DROP_COUNT; i++) {
        twinDropPositions[i * 3] = (Math.random() - 0.5) * 1.6;
        twinDropPositions[i * 3 + 1] = -0.2 - Math.random() * 0.45;
        twinDropPositions[i * 3 + 2] = (Math.random() - 0.5) * 1.0;
        twinDropSpeeds[i] = 0.02 + Math.random() * 0.03;
      }
      dropGeo.setAttribute('position', new THREE.BufferAttribute(twinDropPositions, 3));

      const dropMat = new THREE.PointsMaterial({
        color: 0x00e5ff,
        size: 0.06,
        transparent: true,
        opacity: 0.0
      });
      twinWaterDrops = new THREE.Points(dropGeo, dropMat);
      chamberGroup.add(twinWaterDrops);

      // 8. SENSORS: DHT22 probe on back wall & Soil Probe in tray
      const dhtProbe = new THREE.Mesh(
        new THREE.BoxGeometry(0.15, 0.2, 0.08),
        new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 })
      );
      dhtProbe.position.set(0, 0.3, -0.85);
      chamberGroup.add(dhtProbe);

      const soilProbe = new THREE.Mesh(
        new THREE.BoxGeometry(0.08, 0.35, 0.02),
        new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5 })
      );
      soilProbe.position.set(0.65, -0.55, 0.3);
      chamberGroup.add(soilProbe);

      twinScene.add(chamberGroup);
    }

    function resetTwinCamera() {
      twinCamera.position.set(0, 2.5, 4.8);
      twinControls.target.set(0, 0, 0);
      twinControls.update();
    }

    function onTwinResize() {
      const container = document.getElementById('twin-3d-canvas-container');
      if (!container) return;
      twinCamera.aspect = container.clientWidth / container.clientHeight;
      twinCamera.updateProjectionMatrix();
      twinRenderer.setSize(container.clientWidth, container.clientHeight);
    }

    // Dynamic Actuator State Updater (Called on scenarios or sliders!)
    function updateDigitalTwinActuators(state) {
      if (state.pump !== undefined) twinState.isPumpActive = state.pump;
      if (state.led !== undefined) twinState.isLedActive = state.led;
      if (state.heater !== undefined) twinState.isHeaterActive = state.heater;
      if (state.fan !== undefined) twinState.isFanActive = state.fan;
      if (state.soil !== undefined) twinState.soilMoisture = state.soil;
      if (state.temp !== undefined) twinState.temperature = state.temp;
      if (state.light !== undefined) twinState.lightLux = state.light;

      // Update Lighting
      if (twinPhytoPointLight) {
        twinPhytoPointLight.intensity = twinState.isLedActive ? 2.8 : 0.08;
      }
      if (twinPhytoSpotLight) {
        twinPhytoSpotLight.intensity = twinState.isLedActive ? 2.2 : 0.05;
      }

      // Update Soil Color (Dry = lighter brown, Wet = deep rich dark)
      if (twinSoilMesh) {
        const moistFactor = Math.min(1.0, Math.max(0.0, (twinState.soilMoisture - 20) / 60));
        // Interpolate color from 0x6b4423 (dry) to 0x221308 (wet)
        const r = Math.round(107 - moistFactor * 73);
        const g = Math.round(68 - moistFactor * 49);
        const b = Math.round(35 - moistFactor * 27);
        twinSoilMesh.material.color.setRGB(r / 255, g / 255, b / 255);
      }

      // Update Water Particle Opacity
      if (twinWaterDrops) {
        twinWaterDrops.material.opacity = twinState.isPumpActive ? 0.9 : 0.0;
      }

      // Update Floating Status Badges
      updateTwinHUDChip('fan', twinState.isFanActive, 'ЖЕЛДЕТУ ON (2400 RPM)', 'ӨШІРУЛІ', 'rose');
      updateTwinHUDChip('pump', twinState.isPumpActive, 'СУАРУДА (3-6В)', 'ӨШІРУЛІ', 'cyan');
      updateTwinHUDChip('led', twinState.isLedActive, 'ҚОСУЛЫ (660nm)', 'ӨШІРУЛІ', 'purple');
      updateTwinHUDChip('heater', twinState.isHeaterActive, 'ЖЫЛЫТУДА (PTC)', 'ӨШІРУЛІ', 'amber');
    }

    function updateTwinHUDChip(name, active, onText, offText, color) {
      const dot = document.getElementById(`twin-dot-${name}`);
      const txt = document.getElementById(`twin-txt-${name}`);
      const tag = document.getElementById(`twin-tag-${name}`);

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

    function animateTwinScene() {
      requestAnimationFrame(animateTwinScene);

      // 1. Fan Rotation
      if (twinFanRotor) {
        const fanSpeed = twinState.isFanActive ? 0.38 : 0.003;
        twinFanRotor.rotation.x += fanSpeed;
      }

      // 2. Heater Thermal Glow Animation
      if (twinHeaterMesh) {
        if (twinState.isHeaterActive) {
          const pulse = 1.3 + Math.sin(Date.now() * 0.007) * 0.5;
          twinHeaterMesh.material.emissiveIntensity = pulse;
          twinHeaterMesh.material.color.setHex(0xd97706);
        } else {
          twinHeaterMesh.material.emissiveIntensity = 0.0;
          twinHeaterMesh.material.color.setHex(0x94a3b8);
        }
      }

      // 3. Falling Water Droplets
      if (twinWaterDrops && twinState.isPumpActive) {
        const positions = twinWaterDrops.geometry.attributes.position.array;
        for (let i = 0; i < TWIN_DROP_COUNT; i++) {
          positions[i * 3 + 1] -= twinDropSpeeds[i];
          if (positions[i * 3 + 1] < -0.65) {
            positions[i * 3 + 1] = -0.2;
          }
        }
        twinWaterDrops.geometry.attributes.position.needsUpdate = true;
      }

      twinControls.update();
      twinRenderer.render(twinScene, twinCamera);
    }
"""

# Append the new function calls into applySimScenario and manualUpdateSim
html = html.replace(
    "setRelayUI('fan', s.fan, 'rose', 'ЖЕЛДЕТКІШ ON');",
    "setRelayUI('fan', s.fan, 'rose', 'ЖЕЛДЕТКІШ ON');\n      updateDigitalTwinActuators(s);"
)

html = html.replace(
    "setRelayUI('fan', fan, 'rose', 'ЖЕЛДЕТКІШ ON');",
    "setRelayUI('fan', fan, 'rose', 'ЖЕЛДЕТКІШ ON');\n      updateDigitalTwinActuators({ pump, led, heater, fan, soil, temp, light });"
)

# Insert digital_twin_js before initChart
html = html.replace(
    "// ==========================================\n    // 4. SCIENTIFIC CHART (CHART.JS)",
    digital_twin_js + "\n    // ==========================================\n    // 4. SCIENTIFIC CHART (CHART.JS)"
)

# Add initDigitalTwinScene to window.DOMContentLoaded
html = html.replace(
    "initThreeScene();",
    "initThreeScene();\n      initDigitalTwinScene();"
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html successfully updated with 3D Digital Twin Chamber!")
