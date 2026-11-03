# 💧 AquaGuard - Digital AI Water Purifier Monitoring Cockpit

AquaGuard is an IoT sensor simulation and Explainable Multi-Task Neural Network (MTNN) prognostics dashboard designed for domestic water purifier systems.

---

## 🎨 'Let's Get Digital' Theme

The dashboard has been styled to match the **Let's Get Digital** design:

- **Background:** Gradient blending from luminous sky/azure blue (`#1d4ed8` / `#2563eb`) down into deep obsidian black (`#050811`).
- **Iconic Chamfered Glass Card:** Asymmetrical frosted glass card with a signature rounded chamfer on the top-right corner, subtle inner highlight, and `backdrop-filter: blur(28px)`.
- **Electric Blue Highlights:** Action buttons and primary indicators in `#0066FF`.
- **Typography:**
  - Bold titles with crisp white drop shadows.
  - Uppercase tracked category eyebrow tags (`CREATIVE AI LAB &bull; DIGITAL PORTAL`).
  - High-clarity subtitles and technical telemetry readouts.
- **Glassmorphism Panels:** Translucent multi-sensor telemetry cards with smooth wave sparklines and circular arc meters.

---

## 🎛️ Digital Cockpit Layout

1. **Digital Hero Section:**
   - **Left:** The signature frosted glass card with the `Let's predict & protect` headline, MTNN platform description, and live streaming status pill.
   - **Right:** The multi-stage purifier assembly terminal (Stage 01: Sediment, Stage 02: Carbon Block, Stage 03: RO Membrane) with live frame counter and operating hours.

2. **Sensor Telemetry Cards:**
   - **Differential Pressure** (bar)
   - **Water Flow Rate** (L/min)
   - **Water Turbidity** (NTU)
   - **Water Temperature** (°C)
   - Real-time values, trend indicators, inline wave sparklines, and signal statuses.

3. **AI Prognostic Cards:**
   - **Filter Fault Diagnosis:** Normal / Degrading / Clogged status, confidence %, and distribution.
   - **Remaining Useful Life:** Days to failure with circular arc progress meter.
   - **Anomaly Sentinel:** Sigmoid anomaly classification and probability %.
   - **Cleaning Verification:** Restorative backwash outcome with pre-cleaning vs post-cleaning differentials.

4. **Multi-Sensor Telemetry Chrono-Graph:**
   - Plotly chart featuring electric blue and sky blue spline curves with dark translucent area fills.

5. **Multi-Stage Filter Health Comparison:**
   - Real-time predictions across all 3 purifier stages computed by the MTNN model.

6. **Explainable AI (SHAP):**
   - Global feature importance and summary impact distribution plots.

7. **Alerts & Raw IoT Telemetry:**
   - Dynamic alerts and clean tabular tensor inspector.

---

## 🔐 Database & Authentication

- Persistent SQLite database (`data/aquaguard.db`).
- PBKDF2-HMAC-SHA256 password hashing (100,000 rounds + unique 16-byte salt).
- Default demo administrator credentials:
  - **Username:** `admin`
  - **Password:** `Aquaguard@2026`

---

## 🚀 Launching the Dashboard

1. **Run verification test suite:**
   ```bash
   .\venv\Scripts\python.exe test_auth.py
   .\venv\Scripts\python.exe test_virtual_sensors.py
   .\venv\Scripts\python.exe test_live_prediction.py
   ```

2. **Launch the application:**
   ```bash
   .\venv\Scripts\streamlit.exe run app.py
   ```
   Open `http://localhost:8501` to view the redesigned dashboard.
