import pcbnew
import os

class SimplePlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "motor_pcb"
        self.category = ""
        self.description = "Test"
        self.show_toolbar_button = False # Optional, defaults to False
        self.icon_file_name = ""
        
        self.board = pcbnew.GetBoard()
        
        self.phases = phases = {
            0: "B.Cu",
            1: "In1.Cu",
            2: "In2.Cu",
            3: "In3.Cu",
            4: "In4.Cu",
            5: "In5.Cu",
        }
        
        self.phases = 3
        self.phases_per_layer = 2
        
        self.phase_to_layer = {
            0: ["B.Cu", "In1.Cu"],
            1: ["In2.Cu", "In3.Cu"],
            2: ["In4.Cu", "In5.Cu"]
        }
        
    def draw_phase(self):
        pass
        
    def draw_motor(self):   
        for i in range(self.phases):
            self.draw_phase()
    
    def Run(self):     
        self.draw_motor()
        
        
            
        