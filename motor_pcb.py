import pcbnew
import os

class AdvancedLinearMotor(pcbnew.ActionPlugin):
    pole_width = pcbnew.FromMM(18.75) # The value in FromMM is in mm
    number_of_tracks_per_pole = 10

    def defaults(self):
        self.name = "proba"
        self.category = "A descriptive category name"
        self.description = "A description of the plugin"
        self.show_toolbar_button = False # Optional, defaults to False
        self.icon_file_name = ""
        self.board = pcbnew.GetBoard()
        
        self.net_classes = self.board.GetAllNetClasses()
        self.clearance = self.net_classes['Default'].GetClearance()
        self.track_width = self.net_classes['Default'].GetTrackWidth()
        
        self.vertical_length = pcbnew.FromMM(63) # The value in FromMM is in mm
        self.pole_horizontal_length = 2*self.pole_width #2*18.75 
        
        self.start_track_x = pcbnew.FromMM(56.25)
        self.start_track_y = pcbnew.FromMM(102)
    
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
        
    def Run(self):
        self.set_track_width()
        
        for i in range(5):
            
            
            for j in range(self.number_of_tracks_per_pole):
                offset_x = int((j+0.5) * (self.track_width + self.clearance))
                offset_y = int(j * (self.track_width + self.clearance))
                
                # Generate U-shaped tracks for all poles
                self.create_u_shape(self.start_track_x, self.start_track_y, 
                                    self.pole_horizontal_length, self.vertical_length,
                                    offset_x, offset_y,
                                    self.track_width, pcbnew.B_Cu)
            
            self.start_track_x += self.pole_horizontal_length
                            
        #self.add_track(50, 70, 50, 300, 2, pcbnew.F_Cu)
        pcbnew.Refresh()
        #self.add_track(50,70,50,100)
        
        
AdvancedLinearMotor().register() # Instantiate and register to Pcbnew