import sounddevice as sd                                                                                                                                            
    # Display all available devices and their information                             
print("Available audio devices and their configurations:")                        
print(sd.query_devices())                                                         
                                                                                    
# Attempt to print the default device's supported configurations                  
default_device_index = sd.default.device['input']                                 
default_device_info = sd.query_devices(default_device_index, 'input')             
print("Default input device info:")                                               
print(default_device_info)