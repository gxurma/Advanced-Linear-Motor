import pcbnew
import os

class AdvancedLinearMotor(pcbnew.ActionPlugin):
    number_of_tracks_per_pole = 10
    
    # PCB important dimensions and parameters
    pole_width = pcbnew.FromMM(18.75) # The value in FromMM is in mm
    pole_horizontal_length = 2*pole_width #2*18.75 
    vertical_length = pcbnew.FromMM(63)
    clearance = pcbnew.FromMM(0.5)
    via_diameter = pcbnew.FromMM(1)
    via_drill = pcbnew.FromMM(0.3)
    pole_pairs = 5
    track_width = int((1 / number_of_tracks_per_pole) * pole_width - clearance)
    
    # Origin
    start_track_x = pcbnew.FromMM(56.25)
    start_track_y = pcbnew.FromMM(102)
    
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
    
    def set_track_width(self):
        track_width = int((1 / self.number_of_tracks_per_pole) * self.pole_width - self.clearance)
        self.net_classes['Default'].SetTrackWidth(track_width)
        self.track_width = self.net_classes['Default'].GetTrackWidth()
        
    def add_track(self, start_x, start_y, end_x, end_y, width, layer):
        start_point = pcbnew.VECTOR2I(start_x, start_y)
        end_point = pcbnew.VECTOR2I(end_x, end_y)
    
        track = pcbnew.PCB_TRACK(self.board)
        track.SetStart(start_point)
        track.SetEnd(end_point)
        track.SetLayer(layer)  
        track.SetWidth(width) 
        
        self.board.Add(track)
    
    def add_via(self, pos_x, pos_y, drill_size, via_diam, layer_from, layer_to):
        # Create a via
        via = pcbnew.PCB_VIA(self.board)
        
        # Set the position of the via (in nanometers)
        via.SetPosition(pcbnew.VECTOR2I(pos_x, pos_y))
        
        # Set via properties
        via.SetDrill(drill_size)  # Drill size
        via.SetWidth(via_diam)  # Outer diameter
        via.SetLayerPair(layer_from, layer_to)  # Layer connection
        
        # Connect the via to the specified net
        #via.SetNet(net)
        
        # Add the via to the board
        self.board.Add(via)
    
    def create_u_shape(self, start_x, start_y, length_x, width_y, offset_x, offset_y, track_width, layer):
        # Vertical down line
        self.add_track(
            start_x + offset_x, 
            start_y - offset_y, 
            start_x + offset_x, 
            start_y + width_y - offset_x, 
            track_width, 
            layer
        )
        
        # Horizontal bottom line
        self.add_track(
            start_x + offset_x, 
            start_y + width_y - offset_x, 
            start_x + length_x - offset_x, 
            start_y + width_y - offset_x, 
            track_width, 
            layer
        )
        
        # Vertical up line
        self.add_track(
            start_x + length_x - offset_x, 
            start_y + width_y - offset_x, 
            start_x + length_x - offset_x, 
            start_y - offset_y, 
            track_width, 
            layer
        )
    
    def create_u_shape_with_horizontal_end_line(self, 
        start_x, start_y, length_x, width_y, offset_x, offset_y, track_width, layer):
        # Create U shaped tracks
        self.create_u_shape(start_x, start_y, length_x, width_y, offset_x, offset_y, track_width, layer)
        
        # Endline
        self.add_track(
            start_x + length_x - offset_x, 
            start_y - offset_y,
            start_x + offset_x + self.pole_horizontal_length,
            start_y - offset_y,
            track_width, 
            layer)
    
    def forward_phase(self, start_x, start_y, layer_from, layer_to):
        for i in range(self.pole_pairs):
            for j in range(self.number_of_tracks_per_pole):
                offset_x = int((j+0.5) * (self.track_width + self.clearance))
                offset_y = int(j * (self.track_width + self.clearance))
                
                # Generate U-shaped tracks for all poles
                if i == self.pole_pairs - 1:
                    self.create_u_shape(start_x, start_y,
                                        self.pole_horizontal_length, self.vertical_length,
                                        offset_x, offset_y,
                                        self.track_width, layer_from)
                                        
                    self.add_via(start_x + self.pole_horizontal_length - offset_x, start_y - offset_y,
                                 self.via_drill, self.via_diameter, 
                                 layer_from, layer_to)
                                    
                else:
                    self.create_u_shape_with_horizontal_end_line(start_x, start_y,
                                        self.pole_horizontal_length, self.vertical_length,
                                        offset_x, offset_y,
                                        self.track_width, layer_from)
        
            # Shift start points of u shapes
            start_x += self.pole_horizontal_length
            
    def backward_phase(self, start_x, start_y, layer_from, layer_to):
        for i in range(self.pole_pairs - 1):
            for j in range(self.number_of_tracks_per_pole):
                offset_x = int((j+0.5) * (self.track_width + self.clearance))
                offset_y = int(j * (self.track_width + self.clearance))
                
                if i == 0:
                    # Startline for U-shaped tracks
                    self.add_track(start_x + offset_x, start_y - offset_y,
                                   start_x + self.pole_width + offset_x, start_y - offset_y, 
                                   self.track_width, layer_from)
                                   
                    # Generate U-shaped tracks 
                    self.create_u_shape_with_horizontal_end_line(start_x + self.pole_width, start_y,
                                        self.pole_horizontal_length, self.vertical_length,
                                        offset_x, offset_y,
                                        self.track_width,layer_from)   
                    
                    self.add_via(start_x + offset_x, start_y - offset_y,
                                 self.via_drill, self.via_diameter, 
                                 layer_from, layer_to)     
                                 
                elif i == self.pole_pairs - 2:
                    # Endline
                    self.add_track(start_x + self.pole_width + self.pole_horizontal_length - offset_x, 
                                   start_y - offset_y,
                                   start_x - offset_x + 2*self.pole_horizontal_length, start_y - offset_y,
                                   self.track_width, layer_from)
                                   
                    self.create_u_shape(start_x + self.pole_width, start_y,
                                        self.pole_horizontal_length, self.vertical_length,
                                        offset_x, offset_y,
                                        self.track_width, layer_from)
                else:
                    # Generate U-shaped tracks 
                    self.create_u_shape_with_horizontal_end_line(start_x + self.pole_width, start_y,
                                        self.pole_horizontal_length, self.vertical_length,
                                        offset_x, offset_y,
                                        self.track_width, layer_from)
        
            # Shift start points of u shapes
            start_x += self.pole_horizontal_length
    
    def Run(self):
        self.set_track_width()
        self.forward_phase(self.start_track_x, self.start_track_y, pcbnew.In4_Cu, pcbnew.B_Cu)
        self.backward_phase(self.start_track_x, self.start_track_y, pcbnew.B_Cu, pcbnew.In4_Cu)
        
        pcbnew.Refresh()
        
AdvancedLinearMotor().register() # Instantiate and register to Pcbnew