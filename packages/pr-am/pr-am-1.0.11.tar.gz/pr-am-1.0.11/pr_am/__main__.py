#Project Reality BF2 Artillery Map
#2017/2/21
#Created by Xembie (IGN Darren)

import tkinter as tk
import tkinter.ttk as ttk
import os,pathlib,zipfile,struct,io,math,re,winreg
from PIL import Image,ImageTk

#TODO: Add functionality for zoom.
#TODO: Display current and target positions as well as errors.

class Application:
    def __init__(self,root):
        self.root = root
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\Project Reality\Project Reality: BF2")
            self.default_path,val = winreg.QueryValueEx(key,"InstallDir")
            self.default_path += "\\mods\\pr\\levels\\"
        except:
            self.default_path = os.environ["ProgramFiles(x86)"] + "\\Project Reality\\Project Reality BF2\\mods\\pr\\levels\\"

        self.minimap_size = [0,0]
        self.minimap_primary = [None,None]
        self.minimap_secondary = [None,None]
        self.scale_x = 0.0
        self.scale_y = 0.0
        self.mul_z = 0.0
        self.size = 0
        self.height_offset = 0
        self.mapname = None
        self.default_text = "Select a map. Left click to place your position. Right click to place target position."
        
        self.oval_radius = 5
        self.oval_outline_width = 3

        self.load_maps()
        self.create_widgets()

    def load_maps(self):
        self.maps = {}
        try:
            for p in pathlib.WindowsPath(self.default_path).iterdir():
                if p.is_dir():
                    server_zip_path = str(p) + "\\server.zip"
                    client_zip_path = str(p) + "\\client.zip"
                    if not os.path.isfile(server_zip_path) or \
                        not os.path.isfile(client_zip_path):
                        continue
                    mapname = os.path.basename(str(p))
                    self.maps[mapname] = {}
                    try:
                        with zipfile.ZipFile(server_zip_path) as z:
                            try:
                                with z.open("heightmapprimary.raw") as zf:
                                    self.maps[mapname]["height_map"] = zf.read()
                                    self.maps[mapname]["height_map_size"] = math.sqrt(len(self.maps[mapname]["height_map"]) / 2)
                            except:
                                pass
                            try:
                                with z.open("terrain.con") as zf:
                                    terrain_con_lines = zf.readlines()
                                    for line in terrain_con_lines:
                                        if b"terrain.primaryWorldScale" in line:
                                            values = re.findall("[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?",line.decode())
                                            if len(values) == 3:
                                                try:
                                                    self.maps[mapname]["height_map_size_mult_x"] = float(values[0][0])
                                                    self.maps[mapname]["height_map_size_mult_y"] = float(values[2][0])
                                                    self.maps[mapname]["height_map_size_mult_z"] = float(values[1][0])
                                                except:
                                                    pass
                                                if mapname == "the_falklands":#Special case
                                                    self.maps[mapname]["height_map_size_mult_x"] = 90.0
                                                    self.maps[mapname]["height_map_size_mult_y"] = 90.0
                            except:
                                pass
                    except:
                        pass
                    try:
                        with zipfile.ZipFile(client_zip_path) as z:
                            try:
                                with z.open("hud/minimap/ingamemap.dds") as zf:
                                    self.maps[mapname]["in_game_map"] = zf.read()
                            except:
                                pass
                    except:
                        pass
                    if "height_map" not in self.maps[mapname] or \
                        "height_map_size" not in self.maps[mapname] or \
                        "height_map_size_mult_x" not in self.maps[mapname] or \
                        "height_map_size_mult_y" not in self.maps[mapname] or \
                        "height_map_size_mult_z" not in self.maps[mapname] or \
                        "in_game_map" not in self.maps[mapname]:
                        print("Map " + mapname + " was skipped due to missing files.")
                        self.maps.pop(mapname)
        except:
            print("Could not find maps in \"" + self.default_path + "\"")
    def resize_minimap(self):
        if self.mapname and self.mapname in self.maps:
            minimap_bytes = self.maps[self.mapname]["in_game_map"]
            self.minimap_image = Image.open(io.BytesIO(minimap_bytes))
            self.minimap_image.thumbnail((self.minimap_size[0],self.minimap_size[1]),Image.BICUBIC)
            self.minimap_photo = ImageTk.PhotoImage(self.minimap_image)
            self.minimap_canvas.itemconfig(self.minimap_canvas_image,image = self.minimap_photo)

            #This is a hack because canvas is missing moveto()
            self.minimap_canvas.tk.call(self.minimap_canvas._w,"moveto",self.minimap_canvas_image, \
              (self.minimap_size[0] - self.minimap_image.size[0]) / 2,(self.minimap_size[1] - self.minimap_image.size[0]) / 2)

            self.size = self.maps[self.mapname]["height_map_size"]
            self.scale_x = self.maps[self.mapname]["height_map_size_mult_x"] * self.size
            if self.scale_x < 0.01:
                self.scale_x = 1.0
            self.scale_y = self.maps[self.mapname]["height_map_size_mult_y"] * self.size
            if self.scale_y < 0.01:
                self.scale_y = 1.0

            self.mul_z = self.maps[self.mapname]["height_map_size_mult_z"]
            try:
                temp = math.log(self.mul_z)
            except ZeroDivisionError:
                self.mul_z = 0.003 #Sane value. However, we should not allow use of this minimap.
        self.calculate_trajectory()

    def select_map(self,*args):
        self.mapname = self.maps_var.get()
        if self.mapname == "NO MAPS FOUND!":
            self.mapname = None
        self.resize_minimap()

    def resize(self,event):
        self.minimap_size[0],self.minimap_size[1] = event.width,event.height
        self.resize_minimap()

    def mouse_to_pos(self,x,y):
        size_min = min(self.minimap_size[0],self.minimap_size[1])
        if size_min <= 0:
            return None
        temp_x = (x - self.minimap_size[0] / 2.0) / size_min
        temp_y = (y - self.minimap_size[1] / 2.0) / size_min
        index_x = int((temp_x * self.size) + (self.size / 2.0))
        if index_x < 0:
            return None
        elif index_x >= self.size:
            return None
        index_y = self.size - int((temp_y * self.size) + (self.size / 2.0))#mirror y-axis
        if index_y < 0:
            return None
        elif index_y >= self.size:
            return None
        index = int(index_y * self.size + index_x) * 2
        heighth = self.maps[self.mapname]["height_map"][index:index + 2]
        return [temp_x * self.scale_x,temp_y * self.scale_y,struct.unpack("<H",heighth)[0] * self.mul_z]

    def calculate_trajectory(self):
        primary_pos_values = None
        secondary_pos_values = None
        if self.minimap_primary[0] != None:
            primary_pos_values = self.mouse_to_pos(self.minimap_primary[0],self.minimap_primary[1])
        if self.minimap_secondary[0] != None:
            secondary_pos_values = self.mouse_to_pos(self.minimap_secondary[0],self.minimap_secondary[1])

        self.minimap_canvas.itemconfig(self.minimap_source_oval,state = "hidden")
        self.minimap_canvas.itemconfig(self.minimap_target_oval,state = "hidden")
        
        if self.minimap_primary[0] == None or self.minimap_secondary[0] == None:
            self.info_var.set(self.default_text)
        else:
            self.info_var.set("")

        if primary_pos_values != None:
            self.minimap_canvas.itemconfig(self.minimap_source_oval,state = "normal")
            self.minimap_canvas.tk.call(self.minimap_canvas._w,"moveto", \
                self.minimap_source_oval, \
                self.minimap_primary[0] - (self.oval_radius + 1), \
                self.minimap_primary[1] - (self.oval_radius + 1))
        if secondary_pos_values != None:
            self.minimap_canvas.itemconfig(self.minimap_target_oval,state = "normal")
            self.minimap_canvas.tk.call(self.minimap_canvas._w,"moveto", \
                self.minimap_target_oval, \
                self.minimap_secondary[0] - (self.oval_radius + 1), \
                self.minimap_secondary[1] - (self.oval_radius + 1))
        if primary_pos_values == None or secondary_pos_values == None:
            return
        if self.minimap_primary[0] == None or self.minimap_secondary[0] == None:
            return

        diff_x = self.minimap_secondary[0] - self.minimap_primary[0]
        diff_y = self.minimap_secondary[1] - self.minimap_primary[1]
        angle = math.atan2(diff_x,diff_y) * 180.0 / 3.1415927
        angle = 180.0 - angle
        if angle > 360.0:
            angle -= 360.0

        diff_x = secondary_pos_values[0] - primary_pos_values[0]
        diff_y = secondary_pos_values[1] - primary_pos_values[1]
        diff_z = secondary_pos_values[2] - primary_pos_values[2]
        dist_h = math.sqrt(diff_x * diff_x + diff_y * diff_y)
        dist = math.sqrt(diff_x * diff_x + diff_y * diff_y + diff_z * diff_z)

        diff_z += self.height_offset
        vsqr = 121.306*121.306
        grav = 9.81
        mul = 17.7889
        tosqrt = (vsqr * vsqr) - (grav * ((grav * dist_h * dist_h) + (2 * diff_z * vsqr)));
        if tosqrt < 0.0:
            traj = "Out of range"
        else:
            try:
                traj = int(math.atan((vsqr + math.sqrt(tosqrt)) / (grav * dist_h)) * (180.0 / 3.1415927) * mul)
            except:
                traj = "Shoot straight up"
        extra = ""
        if self.mapname == "the_falklands":
            extra = ",(MAP MISSING HEIGHTMAP)"
        self.info_var.set("Angle:" + str(int(angle)) + ",Dist:" + \
            str(int(dist)) + ",Traj:" + str(traj) + ",Target Z-Delta: " + str(int(diff_z)) + extra)

    def height_change(self,*args):
        try:
            self.height_offset = float(self.height_offset_var.get())
        except:
            self.height_offset = 0.0
        self.calculate_trajectory()

    def primary_click(self,event):
        self.minimap_primary[0],self.minimap_primary[1] = event.x,event.y
        self.calculate_trajectory()

    def secondary_click(self,event):
        self.minimap_secondary[0],self.minimap_secondary[1] = event.x,event.y
        self.calculate_trajectory()

    def create_widgets(self):
        self.top = tk.Frame(self.root)
        self.top.pack(side=tk.TOP,anchor=tk.N,fill=tk.NONE,expand=tk.NO)

        map_names = list(self.maps.keys())
        if len(map_names) == 0:
            map_names = ["NO MAPS FOUND!"]
        self.maps_var = tk.StringVar()
        self.maps_var.trace("w",self.select_map)
        self.maps_menu = ttk.Combobox(self.top,textvariable = self.maps_var,values = map_names)
        self.maps_menu.grid(row=0,column=0)

        self.info_var = tk.StringVar()
        self.info_var.set(self.default_text)
        self.info_label = tk.Label(self.top,textvariable = self.info_var,fg="blue")
        self.info_label.grid(row=0,column=1)

        self.height_offset_label = tk.Label(self.top,text="Target Z-Offset:")
        self.height_offset_label.grid(row=0,column=2)

        self.height_offset_var = tk.StringVar()
        self.height_offset_var.trace("w",self.height_change)
        self.height_offset_entry = tk.Entry(self.top,textvariable = self.height_offset_var)
        self.height_offset_entry.grid(row=0,column=3)

        self.minimap_image = Image.new("RGBA",(0,0))
        self.minimap_photo = ImageTk.PhotoImage(self.minimap_image)
        self.minimap_canvas = tk.Canvas(self.root)
        self.minimap_canvas.bind("<Configure>",self.resize)
        self.minimap_canvas.bind("<Button-1>",self.primary_click)
        self.minimap_canvas.bind("<Button-3>",self.secondary_click)
        self.minimap_canvas.pack(side=tk.BOTTOM,anchor=tk.S,fill=tk.BOTH,expand=tk.YES)

        self.minimap_canvas_image = self.minimap_canvas.create_image( \
            (self.minimap_size[0] - self.minimap_image.size[0]) / 2, \
            (self.minimap_size[1] -  - self.minimap_image.size[0]) / 2, \
            anchor=tk.NW,image = self.minimap_photo)
        self.minimap_source_oval = self.minimap_canvas.create_oval( \
            -self.oval_radius,-self.oval_radius,self.oval_radius,self.oval_radius, \
            width=self.oval_outline_width,outline="green")
        self.minimap_target_oval = self.minimap_canvas.create_oval( \
            -self.oval_radius,-self.oval_radius,self.oval_radius,self.oval_radius, \
            width=self.oval_outline_width,outline="red")
        self.minimap_canvas.itemconfig(self.minimap_source_oval,state = "hidden")
        self.minimap_canvas.itemconfig(self.minimap_target_oval,state = "hidden")
def main(args=None):
    root = tk.Tk()
    root.title("Project Reality Artillery Map by Xembie(Darren)")
    app = Application(root)
    root.geometry("600x600")
    root.mainloop()

if __name__ == "__main__":
    main()
