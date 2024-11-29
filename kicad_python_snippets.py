# Get and set net class properties
import pcbnew
board = pcbnew.GetBoard()
net_classes = board.GetAllNetClasses()
default_net_class = net_classes['Default']
clearance = default_net_class.GetClearance()
default_net_class.SetClearance(250000) #in nm
pcbnew.Refresh()

# Create a new net class
import pcbnew
board = pcbnew.GetBoard()
net_classes = board.GetAllNetClasses()
new_nc = pcbnew.NETCLASS("net_class_name")
new_nc.SetClearance(5000)
net_classes["net_class_name"] = new_nc
net_classes.update()
pcbnew.Refresh()