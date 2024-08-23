# Needs to be copied under C:\Users\%username\Documents\KiCad\8.0\scripting\plugins
# Pcbnew -> tools/plugins
import pcbnew
import os

class AdvancedLinearMotor(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "advance_linear_motor"
        self.category = ""
        self.description = "Test"
        self.show_toolbar_button = False # Optional, defaults to False
        self.icon_file_name = ""
        
        self.board = pcbnew.GetBoard()
        
        self.phases = 3
        self.phases_per_layer = 2
        
        self.phases = phases = {
            0: "B.Cu",
            1: "In1.Cu",
            2: "In2.Cu",
            3: "In3.Cu",
            4: "In4.Cu",
            5: "In5.Cu",
        }
        
        self.phase_to_layer = {
            0: ["B.Cu", "In1.Cu"],
            1: ["In2.Cu", "In3.Cu"],
            2: ["In4.Cu", "In5.Cu"]
        }
        
        self.start_connector = "J1"
        
    def draw_base_tracks(self):
        component = board.FindFootprintByReference(self.start_connector)
        
        # 2
        pad = component.FindPadByNumber("2")
        start_point = pad.GetPosition()
        end_point = pcbnew.VECTOR2I(start_point.x, start_point.y - pcbnew.FromMM(10))
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(start_point)
        track.SetEnd(end_point)
        track.SetLayer(pcbnew.In2_Cu)  
        track.SetWidth(pcbnew.FromMM(2))  
        
        track.SetNetCode(pad.GetNet().GetNetCode())

        board.Add(track)

    def draw_phase(self):
        pass
        
    def draw_motor(self):   
        self.draw_base_tracks()
    
    def Run(self):     
        self.draw_motor()
        pcbnew.Refresh()
        
SimplePlugin().register()
        
        
            
        