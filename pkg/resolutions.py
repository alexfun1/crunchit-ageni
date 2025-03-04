from pkg.globals import *


def apply_resolution(resolutions_selector):
    if not resolutions_selector:
        return 64,64  # setting default resolution if no resolution is selected
    
    resolutions = RESOLUTIONS.get(resolutions_selector)
    if resolutions:
        return resolutions["width"], resolutions["height"]
    else:
        return 64,64