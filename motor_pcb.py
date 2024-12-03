import pcbnew
import os

DEFAULT_VIA_DRILL = pcbnew.FromMM(0.3)
DEFAULT_VIA_DIAMETER = pcbnew.FromMM(1)
DEFAULT_CLEARANCE = pcbnew.FromMM(0.5)

class AdvancedLinearMotor(pcbnew.ActionPlugin):
    number_of_tracks_per_pole = 10
    
    # PCB important dimensions and parameters
    pcb_length_for_tracks = pcbnew.FromMM(150)
    pcb_height_for_tracks = pcbnew.FromMM(63)
    no_of_poles = 8
    no_of_periods = 4
    no_of_phases = 3
    
    clearance = pcbnew.FromMM(0.5)
    
    # Derived values for the given parameters
    pole_length = int(pcb_length_for_tracks / no_of_poles)
    period_length = int(pcb_length_for_tracks / no_of_periods) 
    phase_shift = int(pole_length / no_of_phases) #pcbnew.FromMM(5)
    
    track_width = int((1 / number_of_tracks_per_pole) * pole_length - clearance)
    via_diameter = int(0.8*track_width)
    via_drill = int(0.25*track_width)
    
    
    # Origin
    start_track_x = pcbnew.FromMM(56.25)
    start_track_y = pcbnew.FromMM(102)
    
    # Phase information
    phase_informations = [
        {"layer_from": pcbnew.F_Cu, "layer_to": pcbnew.In1_Cu, 
        "phase_shift": 0, 
        "net": "Net-(J1-Pin_3)", 
        "start_modul": "J1", "start_pad":"3", "end_modul": "R1", "end_pad": "1"},
        {"layer_from": pcbnew.In2_Cu, "layer_to": pcbnew.In3_Cu, 
        "phase_shift": phase_shift, 
        "net": "Net-(J1-Pin_2)", 
        "start_modul": "J1", "start_pad":"2","end_modul": "R2", "end_pad": "1"},
        {"layer_from": pcbnew.In4_Cu, "layer_to": pcbnew.B_Cu, 
        "phase_shift": -phase_shift, 
        "net": "Net-(J1-Pin_1)", 
        "start_modul": "J1", "start_pad":"1","end_modul": "R3", "end_pad": "1"}]
    
    def defaults(self):
        self.name = "proba"
        self.category = "A descriptive category name"
        self.description = "A description of the plugin"
        self.show_toolbar_button = True # Optional, defaults to False
        self.icon_file_name = ""
        self.board = pcbnew.GetBoard()
        
        # Set net based on parameters
        self.net_classes = self.board.GetAllNetClasses()
        self.net_classes['Default'].SetClearance(self.clearance)
        self.net_classes['Default'].SetViaDiameter(self.via_diameter)
        self.net_classes['Default'].SetViaDrill(self.via_drill)
        self.net_classes['Default'].SetViaDrill(self.via_drill)
        self.net_classes['Default'].SetTrackWidth(self.track_width)
        
    def add_track(self, start_x, start_y, end_x, end_y, width, layer, net):
        track = pcbnew.PCB_TRACK(self.board)
        
        track.SetStart(pcbnew.VECTOR2I(start_x, start_y))
        track.SetEnd(pcbnew.VECTOR2I(end_x, end_y))
        track.SetLayer(layer)  
        track.SetWidth(width) 
        track.SetNet(self.board.FindNet(net))
        
        self.board.Add(track)
    
    def add_via(self, pos_x, pos_y, drill_size=DEFAULT_VIA_DRILL, via_diam=DEFAULT_VIA_DIAMETER, layer_from=None, layer_to=None, net=None):
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
                        
    def create_vertical_track(self, start_x, start_y, end_y, track_width, layer, net):
        """Creates a vertical track."""
        self.add_track(start_x, start_y, start_x, end_y, track_width, layer, net)
        
    def create_horizontal_track(self, start_x, start_y, end_x, track_width, layer, net):
        """Creates a horizontal track."""
        self.add_track(start_x, start_y, end_x, start_y, track_width, layer, net)

    def create_u_shape(self, start_x, start_y, offset_x, offset_y, track_width, layer, net):
        """Creates a U-shaped track."""
        self.create_vertical_track(start_x + offset_x, start_y - offset_y,
                                   start_y + self.pcb_height_for_tracks - offset_x, 
                                   track_width, layer, net)
                                   
        self.create_horizontal_track(start_x + offset_x, start_y + self.pcb_height_for_tracks - offset_x,
                                     start_x + self.period_length - offset_x, 
                                     track_width, layer, net)
                                     
        self.create_vertical_track(start_x + self.period_length - offset_x, start_y + self.pcb_height_for_tracks - offset_x,
                                   start_y - offset_y, 
                                   track_width, layer, net)
    
    def forward_phase(self, start_x, start_y, phase_shift, layer_from, layer_to, start_module, start_pad, net):
        start_x += phase_shift
        for i in range(self.no_of_periods + 1):
            for j in range(self.number_of_tracks_per_pole):
                offset_x = int((j+0.5) * (self.track_width + self.clearance))
                offset_y = int(j * (self.track_width + self.clearance))
                
                # Kezdés
                if (i == 0 and j==0):
                    start_position = self.get_module_pad_position(start_module, start_pad)
                        
                    # Vertical
                    self.add_track(start_x + offset_x, start_y - offset_y,
                                   start_x + offset_x, start_position.y,
                                   min(self.track_width, pcbnew.FromMM(2)), layer_from, net) 

                    # Via
                    if layer_from != pcbnew.F_Cu:
                        self.add_via(start_x + offset_x, start_position.y,
                                     pcbnew.FromMM(0.3), pcbnew.FromMM(1),
                                     layer_from, pcbnew.F_Cu, net)

                    # Horizontal
                    self.add_track(start_x + offset_x, start_position.y,
                                   start_position.x, start_position.y,
                                   min(self.track_width, pcbnew.FromMM(2)), pcbnew.F_Cu, net)
                                   
                # Generate U-shaped tracks for all poles
                self.create_u_shape(start_x, start_y,
                                    offset_x, offset_y,
                                    self.track_width, layer_from, net)
                
                # Place Via-s at the very end of the tracks
                if i == self.no_of_periods:
                    self.add_via(start_x + self.period_length - offset_x, start_y - offset_y,
                                 self.via_drill, self.via_diameter, 
                                 layer_from, layer_to, net)
                                    
                else:       
                    # Place horizontal end lines for the U-shaped tracks             
                    self.add_track(start_x + self.period_length - offset_x, start_y - offset_y,
                                   start_x + offset_x + self.period_length, start_y - offset_y,
                                   self.track_width, layer_from, net)

            # Shift start points of the U-shaped tracks
            start_x += self.period_length
            
    def backward_phase(self, start_x, start_y, phase_shift, layer_from, layer_to, end_module, end_pad, net):
        start_x += phase_shift
        for i in range(self.no_of_periods):
            for j in range(self.number_of_tracks_per_pole):
                offset_x = int((j+0.5) * (self.track_width + self.clearance))
                offset_y = int(j * (self.track_width + self.clearance))
                
                if i == 0:
                    # Startline for U-shaped tracks
                    self.add_track(start_x + offset_x, start_y - offset_y,
                                   start_x + self.pole_length + offset_x, start_y - offset_y, 
                                   self.track_width, layer_to, net)
                                   
                    # Generate U-shaped tracks                                        
                    self.create_u_shape(start_x + self.pole_length, start_y,
                                        offset_x, offset_y,
                                        self.track_width, layer_to, net)
                    # Endline
                    self.add_track(start_x + self.pole_length + self.period_length - offset_x, start_y - offset_y,
                                   start_x + self.pole_length + offset_x + self.period_length, start_y - offset_y,
                                   self.track_width, layer_to, net)
                    
                    self.add_via(start_x + offset_x, start_y - offset_y,
                                 self.via_drill, self.via_diameter, 
                                 layer_from, layer_to, net)     
                    # Lezárás
                    if j == self.number_of_tracks_per_pole - 1:
                        end_position = self.get_module_pad_position(end_module, end_pad)
                        
                        # Vertical Up
                        self.add_track(start_x + offset_x, start_y - offset_y,
                                       start_x + offset_x, end_position.y,
                                       min(self.track_width, pcbnew.FromMM(2)), layer_to, net) 
                                       
                        
                        # Via
                        if layer_to != pcbnew.F_Cu:
                            self.add_via(start_x + offset_x, end_position.y,
                                         pcbnew.FromMM(0.3), pcbnew.FromMM(1),
                                         layer_to, pcbnew.F_Cu, net)

                        # Horizontal Right
                        self.add_track(start_x + offset_x, end_position.y,
                                       end_position.x, end_position.y,
                                       min(self.track_width, pcbnew.FromMM(2)), pcbnew.F_Cu, net)   
                                       
                elif i == self.no_of_periods - 1:
                    # Endline for U-shaped tracks
                    self.add_track(start_x + self.pole_length + self.period_length - offset_x, 
                                   start_y - offset_y,
                                   start_x - offset_x + 2*self.period_length, start_y - offset_y,
                                   self.track_width, layer_to, net)
                                   
                    self.create_u_shape(start_x + self.pole_length, start_y,
                                        offset_x, offset_y,
                                        self.track_width, layer_to, net)
                    
                        
                else:
                    # Generate U-shaped tracks 
                    self.create_u_shape(start_x + self.pole_length, start_y,
                                        offset_x, offset_y,
                                        self.track_width, layer_to, net)
                    
                    self.add_track(start_x + self.pole_length + self.period_length - offset_x, start_y - offset_y,
                                    start_x + self.pole_length + offset_x + self.period_length, start_y - offset_y,
                                    self.track_width, layer_to, net)
        
            # Shift start points of u shapes
            start_x += self.period_length
            
    def phase(self, start_x, start_y, phase_shift, layer_from, layer_to, start_module, start_pad, end_module, end_pad, net):
        self.forward_phase(start_x, start_y, phase_shift, layer_from, layer_to, start_module, start_pad, net)
        self.backward_phase(start_x, start_y, phase_shift, layer_from, layer_to, end_module, end_pad, net)
    
    def process_phase(self, phase):
        """Processes a single phase."""
        self.forward_phase(self.start_track_x, self.start_track_y, phase["phase_shift"], 
                           phase["layer_from"], phase["layer_to"], 
                           phase["start_modul"], phase["start_pad"], phase["net"])
                           
        self.backward_phase(self.start_track_x, self.start_track_y, phase["phase_shift"], 
                            phase["layer_from"], phase["layer_to"], 
                            phase["end_modul"], phase["end_pad"], phase["net"])

    def Run(self):
        for phase in self.phase_informations:
            self.process_phase(phase)
            
        pcbnew.Refresh()
        
AdvancedLinearMotor().register() # Instantiate and register to Pcbnew