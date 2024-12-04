import pcbnew
import os

CONFIG = {"number_of_tracks_per_pole": 10,  # Tracks in one pole
          "clearance_mm": 0.25}             # Minimum spacing between tracks (in mm)

class AdvancedLinearMotor(pcbnew.ActionPlugin): 
    def defaults(self):
        """
        Initialize the plugin with defaults and board setup.
        """
        self.name = "Advanced Linear Motor"
        self.category = "PCB Automation"
        self.description = "Automates track and via generation for linear motors."
        self.show_toolbar_button = True # Optional, defaults to False
        self.icon_file_name = ""
        self.board = pcbnew.GetBoard()
        
        self.number_of_tracks_per_pole = CONFIG["number_of_tracks_per_pole"]
        self.clearance = pcbnew.FromMM(CONFIG["clearance_mm"])
        
        # PCB important dimensions and parameters
        self.pcb_length_for_tracks = pcbnew.FromMM(150)
        self.pcb_height_for_tracks = pcbnew.FromMM(63)
        self.no_of_poles = 8
        self.no_of_periods = 4
        self.no_of_phases = 3
            
        # Derived values for the given parameters
        self.pole_length = int(self.pcb_length_for_tracks / self.no_of_poles)
        self.period_length = int(self.pcb_length_for_tracks / self.no_of_periods) 
        self.phase_shift = int(self.pole_length / self.no_of_phases) #pcbnew.FromMM(5)
        
        self.track_width = int((1 / self.number_of_tracks_per_pole) * self.pole_length - self.clearance)
        self.via_diameter = int(0.6*self.track_width)
        self.via_drill = int(0.2*self.track_width)
        
        # Origin
        self.start_track_x = pcbnew.FromMM(48.8757)
        self.start_track_y = pcbnew.FromMM(82.2087)
        
        # Phase information
        self.phase_informations = [
            {"layer_from": pcbnew.F_Cu, "layer_to": pcbnew.In1_Cu, 
            "phase_shift": 0, 
            "net": "Net-(J1-Pin_3)", 
            "start_modul": "J1", "start_pad":"3", "end_modul": "R3", "end_pad": "1"},
            {"layer_from": pcbnew.In2_Cu, "layer_to": pcbnew.In3_Cu, 
            "phase_shift": self.phase_shift, 
            "net": "Net-(J1-Pin_2)", 
            "start_modul": "J1", "start_pad":"2","end_modul": "R2", "end_pad": "1"},
            {"layer_from": pcbnew.In4_Cu, "layer_to": pcbnew.B_Cu, 
            "phase_shift": -self.phase_shift, 
            "net": "Net-(J1-Pin_1)", 
            "start_modul": "J1", "start_pad":"1","end_modul": "R1", "end_pad": "1"}]
        
        # Set net based on parameters
        self.net_classes = self.board.GetAllNetClasses()
        default_netclass = self.net_classes.get("Default", None)
        if default_netclass:
            default_netclass.SetClearance(self.clearance)
            default_netclass.SetViaDiameter(self.via_diameter)
            default_netclass.SetViaDrill(self.via_drill)
            default_netclass.SetTrackWidth(self.track_width)
            
    def delete_tracks(self):
        """Deletes all tracks """
        tracks = self.board.GetTracks()

        for track in tracks:
            self.board.Remove(track)

        pcbnew.Refresh()
    
    def add_track(self, start_x, start_y, end_x, end_y, width, layer, net):
        """
        Adds a track to the PCB.
        """
        # Validate net
        net_obj = self.board.FindNet(net)
        if not net_obj:
            raise ValueError(f"Net '{net}' not found.")
            
        track = pcbnew.PCB_TRACK(self.board)
        track.SetStart(pcbnew.VECTOR2I(start_x, start_y))
        track.SetEnd(pcbnew.VECTOR2I(end_x, end_y))
        track.SetLayer(layer)  
        track.SetWidth(width) 
        track.SetNet(self.board.FindNet(net))
        self.board.Add(track)
    
    def add_via(self, pos_x, pos_y, drill_size, via_diam, layer_from, layer_to, net):
        """
        Adds a via to the PCB.
        """
        # Validate net
        net_obj = self.board.FindNet(net)
        if not net_obj:
            raise ValueError(f"Net '{net}' not found.")
            
        # Validate and set layer pair
        if layer_from is None or layer_to is None:
            raise ValueError("Layer pair must be specified for the via.")   
         
        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition(pcbnew.VECTOR2I(pos_x, pos_y))
        via.SetDrill(drill_size)
        via.SetViaType(pcbnew.VIATYPE_BLIND_BURIED)
        via.SetWidth(via_diam)
        via.SetLayerPair(layer_from, layer_to)
        via.SetNet(self.board.FindNet(net))
        self.board.Add(via)
    
    def get_module_pad_position(self, module_name, pad_name):
        for module in self.board.GetFootprints():
            if module.GetReference() == module_name:  
                for pad in module.Pads():
                    if pad.GetPadName() == pad_name:  
                        return pad.GetPosition()
                        
        raise ValueError(f"Module '{module_name}' or Pad '{pad_name}' not found.")
                        
    def create_vertical_track(self, start_x, start_y, end_y, track_width, layer, net):
        """Creates a vertical track."""
        self.add_track(start_x, start_y, start_x, end_y, track_width, layer, net)
        
    def create_horizontal_track(self, start_x, start_y, end_x, track_width, layer, net):
        """Creates a horizontal track."""
        self.add_track(start_x, start_y, end_x, start_y, track_width, layer, net)

    def create_u_shape(self, start_x, start_y, offset_x, offset_y, track_width, layer, net):
        """Creates a U-shaped track."""
        if offset_x < 0 or offset_y < 0:
            raise ValueError("Offsets must be non-negative.")
            
        self.create_vertical_track(start_x + offset_x, start_y - offset_y,
                                   start_y + self.pcb_height_for_tracks - offset_x, 
                                   track_width, layer, net)
                                   
        self.create_horizontal_track(start_x + offset_x, start_y + self.pcb_height_for_tracks - offset_x,
                                     start_x + self.period_length - offset_x, 
                                     track_width, layer, net)
                                     
        self.create_vertical_track(start_x + self.period_length - offset_x, start_y + self.pcb_height_for_tracks - offset_x,
                                   start_y - offset_y, 
                                   track_width, layer, net)
                                   
    def create_horizontal_connection(self, start_x, start_y, offset_x, offset_y, layer, net):
        """Create horizontal connection lines between U-shaped tracks."""
        self.add_track(start_x + self.period_length - offset_x, start_y - offset_y,
                       start_x + self.period_length + offset_x, start_y - offset_y,
                       self.track_width, layer, net)
                       
    def process_phase_connection(self, start_x, start_y, offset_x, offset_y, layer, connection_module, connection_pad, net):
        """ Processes the connection of a phase"""
        connection_position = self.get_module_pad_position(connection_module, connection_pad)
        connection_track_width =  min(self.track_width, pcbnew.FromMM(2))
        
        # Vertical track
        self.create_vertical_track(start_x + offset_x, start_y - offset_y, connection_position.y, connection_track_width, layer, net)

        # Via
        if layer != pcbnew.F_Cu:
            self.add_via(start_x + offset_x, connection_position.y,
                         int(0.2*connection_track_width), int(0.6*connection_track_width),
                         layer, pcbnew.F_Cu, net)

        # Horizontal track
        self.create_horizontal_track(start_x + offset_x, connection_position.y, connection_position.x, connection_track_width, pcbnew.F_Cu, net)

    def calculate_offsets(self, track_index):
        """Calculate horizontal and vertical offsets for a track."""
        offset_x = int((track_index + 0.5) * (self.track_width + self.clearance))
        offset_y = int(track_index * (self.track_width + self.clearance))
        return offset_x, offset_y
        
    def forward_phase(self, start_x, start_y, phase_shift, layer_from, layer_to, start_module, start_pad, net):
        start_x += phase_shift
        for period_index in range(self.no_of_periods + 1):
            for track_index in range(self.number_of_tracks_per_pole):
                # Calculate offset for tracks
                offset_x, offset_y = self.calculate_offsets(track_index)
                
                # Generate U-shaped tracks for all poles
                self.create_u_shape(start_x, start_y,
                                    offset_x, offset_y,
                                    self.track_width, layer_from, net)
                # Phase start
                if (period_index == 0 and track_index==0):
                    pass
                    #self.process_phase_connection(start_x, start_y, offset_x, offset_y, layer_from, start_module, start_pad, net)               
                
                # Place Via-s at the very end of the tracks
                if period_index == self.no_of_periods:
                    self.add_via(start_x + self.period_length - offset_x, start_y - offset_y,
                                 self.via_drill, self.via_diameter, 
                                 layer_from, layer_to, net)
                                    
                else:              
                    # Add horizontal connections between U-shaped tracks
                    self.create_horizontal_connection(start_x, start_y, offset_x, offset_y, layer_from, net)

            # Shift start points of the U-shaped tracks
            start_x += self.period_length
            
    def backward_phase(self, start_x, start_y, phase_shift, layer_from, layer_to, end_module, end_pad, net):
        start_x += phase_shift
        for period_index in range(self.no_of_periods):
            for track_index in range(self.number_of_tracks_per_pole):
                # Calculate offset for tracks
                offset_x, offset_y = self.calculate_offsets(track_index)
                
                # Generate U-shaped tracks   
                self.create_u_shape(start_x + self.pole_length, start_y,
                                    offset_x, offset_y,
                                    self.track_width, layer_to, net)
                                        
                # End tracks for backward phase
                if period_index == 0:
                    # Startline for U-shaped track
                    self.create_horizontal_track(start_x + offset_x, start_y - offset_y, 
                                                 start_x + self.pole_length + offset_x, 
                                                 self.track_width, layer_to, net)

                    # Endline for U-shaped track
                    self.create_horizontal_track(start_x + self.pole_length + self.period_length - offset_x, start_y - offset_y, 
                                                 start_x + self.pole_length + offset_x + self.period_length, 
                                                 self.track_width, layer_to, net)
                                   
                    # Place Via-s at the very end of the tracks
                    self.add_via(start_x + offset_x, start_y - offset_y,
                                 self.via_drill, self.via_diameter, 
                                 layer_from, layer_to, net)     
                                 
                    # Backward phase end
                    if track_index == self.number_of_tracks_per_pole - 1:
                        pass
                        #self.process_phase_connection(start_x, start_y, offset_x, offset_y, layer_to, end_module, end_pad, net)
                        
                # Start tracks for backward phase                       
                elif period_index == self.no_of_periods - 1:
                    # Startline for U-shaped tracks
                    self.add_track(start_x + self.pole_length + self.period_length - offset_x, 
                                   start_y - offset_y,
                                   start_x + 2*self.period_length - offset_x, 
                                   start_y - offset_y,
                                   self.track_width, layer_to, net)                        
                
                else:          
                    self.create_horizontal_connection(start_x + self.pole_length, start_y, offset_x, offset_y, layer_to, net)
                    
            # Shift start points of the U-shaped tracks
            start_x += self.period_length

    def process_phase(self, phase):
        """Processes a single phase."""
        print(f"Processing phase with net: {phase['net']}")
        self.forward_phase(self.start_track_x, self.start_track_y, phase["phase_shift"], 
                           phase["layer_from"], phase["layer_to"], 
                           phase["start_modul"], phase["start_pad"], phase["net"])
                           
        self.backward_phase(self.start_track_x, self.start_track_y, phase["phase_shift"], 
                            phase["layer_from"], phase["layer_to"], 
                            phase["end_modul"], phase["end_pad"], phase["net"])

    def Run(self):
        """Entry point for the plugin."""
        print("Starting Advanced Linear Motor Plugin...")
        self.delete_tracks()
        try:
            for phase in self.phase_informations:
                self.process_phase(phase)
            print("All phases processed successfully.")
        except Exception as e:
            print(f"Error during processing: {e}")
        finally:
            pcbnew.Refresh()
        
AdvancedLinearMotor().register() # Instantiate and register to Pcbnew