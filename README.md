# Advanced-Linear-Motor
An advanced design for linear motors. Uses also some advanced algorithms and Python scripts to optimize the copper usage, resistance, and heat dissipation.

# Design goals
- 6 layer PCBs
- 70µm or 105µm thick copper
- Maximized copper packing for efficiency
- 3 phases
- 1 phase spans 2 layers
- Minimize the number of vias

# Features
- Automated track generation using Python scripting
- Multi-layer support with blind and buried vias
- Dynamic phase shifting for optimized layout
- Configurable parameters for:
  - Number of poles, phases, and periods
  - Track width and clearance
  - Via diameter and drill sizes
- Error handling with debug logging

# Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/gxurma/Advanced-Linear-Motor.git
   ```
2. Place the plugin in KiCad's scripting plugins directory:
   - Windows: `%APPDATA%/kicad/scripting/plugins/`
   - Linux: `~/.local/share/kicad/scripting/plugins/`
   - macOS: `~/Library/Application Support/kicad/scripting/plugins/`
3. Restart KiCad to load the plugin.

# Usage
1. Open your PCB project in KiCad.
2. Launch the plugin from **Tools > External Plugins**.
3. Adjust the design parameters as needed:
   - Track width, clearance, via dimensions
   - Number of poles and phases
4. Click **Run Plugin** to generate the layout.

# Contribution
Contributions are welcome! Fork the repository, make your changes, and open a pull request. Ensure your code follows the existing structure and coding standards.

# License
This project is licensed under the MIT License.