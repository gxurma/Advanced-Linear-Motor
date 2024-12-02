import pcbnew
import os

class AdvancedLinearMotor(pcbnew.ActionPlugin):
    number_of_tracks_per_pole = 5
    
    # PCB important dimensions and parameters
    pcb_length_for_tracks = pcbnew.FromMM(150)
    pcb_height_for_tracks = pcbnew.FromMM(63)
    no_of_poles = 8
    no_of_periods = 4
    no_of_phases = 3
    
    clearance = pcbnew.FromMM(0.5)
    via_diameter = pcbnew.FromMM(1)
    via_drill = pcbnew.FromMM(0.3)
    
    pole_length = int(pcb_length_for_tracks / no_of_poles)
    period_length = int(pcb_length_for_tracks / no_of_periods) 
    phase_shift = pcbnew.FromMM(5)#int(period_length / no_of_phases)
    
    pole_pairs = 5 # Ezzel mi a brét csináljunk?
    track_width = int((1 / number_of_tracks_per_pole) * pole_length - clearance)
    
    # Origin
    start_track_x = pcbnew.FromMM(56.25)
    start_track_y = pcbnew.FromMM(102)
    
    # Phase information
    phase_informations = [
        {"layer_from": pcbnew.F_Cu, "layer_to": pcbnew.In1_Cu, 
        "phase_shift": 0, 
        "net": "Net-(J1-Pin_3)", 
        "start_modul": "J1", "start_pad":"3", "end_module": "R1", "end_pad": "1"},
        {"layer_from": pcbnew.In2_Cu, "layer_to": pcbnew.In3_Cu, 
        "phase_shift": phase_shift, 
        "net": "Net-(J1-Pin_2)", 
        "start_modul": "J1", "start_pad":"2","end_module": "R2", "end_pad": "1"},
        {"layer_from": pcbnew.In4_Cu, "layer_to": pcbnew.B_Cu, 
        "phase_shift": -phase_shift, 
        "net": "Net-(J1-Pin_1)", 
        "start_modul": "J1", "start_pad":"1","end_module": "R3", "end_pad": "1"}]
    
    def defaults(self):
        self.name = "proba"
        self.category = "A descriptive category name"
        self.description = "A description of the plugin"
        self.show_toolbar_button = True # Optional, defaults to False
        self.icon_file_name = ""
        self.board = pcbnew.GetBoard()
        
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
    
    def add_via(self, pos_x, pos_y, drill_size, via_diam, layer_from, layer_to, net):
        # Create a via
        via = pcbnew.PCB_VIA(self.board)
     
        via.SetPosition(pcbnew.VECTOR2I(pos_x, pos_y))
        via.SetDrill(drill_size)
        via.SetViaType(pcbnew.VIATYPE_BLIND_BURIED)
        via.SetWidth(via_diam)
        via.SetLayerPair(layer_from, layer_to)
        via.SetNet(self.board.FindNet(net))
        
        self.board.Add(via)
    
    def create_u_shape(self, start_x, start_y, length_x, width_y, offset_x, offset_y, track_width, layer, net):
        # Vertical down line
        self.add_track(
            start_x + offset_x, 
            start_y - offset_y, 
            start_x + offset_x, 
            start_y + width_y - offset_x, 
            track_width, 
            layer,
            net)
        
        # Horizontal bottom line
        self.add_track(
            start_x + offset_x, 
            start_y + width_y - offset_x, 
            start_x + length_x - offset_x, 
            start_y + width_y - offset_x, 
            track_width, 
            layer,
            net)
        
        # Vertical up line
        self.add_track(
            start_x + length_x - offset_x, 
            start_y + width_y - offset_x, 
            start_x + length_x - offset_x, 
            start_y - offset_y, 
            track_width, 
            layer,
            net)
    
    def create_u_shape_with_horizontal_end_line(self, 
        start_x, start_y, length_x, width_y, offset_x, offset_y, track_width, layer, net):
        # Create U shaped tracks
        self.create_u_shape(start_x, start_y, length_x, width_y, offset_x, offset_y, track_width, layer, net)
        
        # Endline
        self.add_track(
            start_x + length_x - offset_x, 
            start_y - offset_y,
            start_x + offset_x + self.period_length,
            start_y - offset_y,
            track_width, 
            layer,
            net)
    
    def forward_phase(self, start_x, start_y, phase_shift, layer_from, layer_to, net):
        start_x += phase_shift
        for i in range(self.no_of_periods + 1):
            for j in range(self.number_of_tracks_per_pole):
                offset_x = int((j+0.5) * (self.track_width + self.clearance))
                offset_y = int(j * (self.track_width + self.clearance))
                
                # Generate U-shaped tracks for all poles
                if i == self.no_of_periods:
                    self.create_u_shape(start_x, start_y,
                                        self.period_length, self.pcb_height_for_tracks,
                                        offset_x, offset_y,
                                        self.track_width, layer_from, net)
                                        
                    self.add_via(start_x + self.period_length - offset_x, start_y - offset_y,
                                 self.via_drill, self.via_diameter, 
                                 layer_from, layer_to, net)
                                    
                else:
                    self.create_u_shape_with_horizontal_end_line(start_x, start_y,
                                        self.period_length, self.pcb_height_for_tracks,
                                        offset_x, offset_y,
                                        self.track_width, layer_from, net)
        
            # Shift start points of u shapes
            start_x += self.period_length
            
    def backward_phase(self, start_x, start_y, phase_shift, layer_from, layer_to, net):
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
                    self.create_u_shape_with_horizontal_end_line(start_x + self.pole_length, start_y,
                                        self.period_length, self.pcb_height_for_tracks,
                                        offset_x, offset_y,
                                        self.track_width, layer_to, net)   
                    
                    self.add_via(start_x + offset_x, start_y - offset_y,
                                 self.via_drill, self.via_diameter, 
                                 layer_from, layer_to, net)     
                                 
                elif i == self.no_of_periods - 1:
                    # Endline
                    self.add_track(start_x + self.pole_length + self.period_length - offset_x, 
                                   start_y - offset_y,
                                   start_x - offset_x + 2*self.period_length, start_y - offset_y,
                                   self.track_width, layer_to, net)
                                   
                    self.create_u_shape(start_x + self.pole_length, start_y,
                                        self.period_length, self.pcb_height_for_tracks,
                                        offset_x, offset_y,
                                        self.track_width, layer_to, net)
                else:
                    # Generate U-shaped tracks 
                    self.create_u_shape_with_horizontal_end_line(start_x + self.pole_length, start_y,
                                        self.period_length, self.pcb_height_for_tracks,
                                        offset_x, offset_y,
                                        self.track_width, layer_to, net)
        
            # Shift start points of u shapes
            start_x += self.period_length
            
    def phase(self, start_x, start_y, phase_shift, layer_from, layer_to, net):
        self.forward_phase(start_x, start_y, phase_shift, layer_from, layer_to, net)
        self.backward_phase(start_x, start_y, phase_shift, layer_from, layer_to, net)
        
    def Run(self):
        for phase_information in self.phase_informations:
            layer_from = phase_information["layer_from"]
            layer_to = phase_information["layer_to"]
            net = phase_information["net"]
            phase_shift = phase_information["phase_shift"]
            
            self.phase(self.start_track_x, self.start_track_y, phase_shift, layer_from, layer_to, net)
            
        pcbnew.Refresh()
        
AdvancedLinearMotor().register() # Instantiate and register to Pcbnew