import cv2
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import numpy as np
import matplotlib.pyplot as plt

from src.services.graphics_extensions.opencv import helpers

def animate1():
    img = cv2.imread('./res/plane.png')
    height, width, c = img.shape
    
    i = 0
    
    while True:
        i += 1
        
        # divided the image into left and right part
        # like list concatenation we concatenated
        # right and left together
        l = img[:, :(i % width)]
        r = img[:, (i % width):]
    
        img1 = np.hstack((r, l))
        
        # this function will concatenate
        # the two matrices
        cv2.imshow('animation', img1)
    
        if cv2.waitKey(1) == ord('q'):
        
            # press q to terminate the loop
            cv2.destroyAllWindows()
            break

def make_moving_object_frame(clip, speed=150, object_path='./res/images.png', direction='right'):
    if direction == 'right':
        multiplier = -1
    else:
        multiplier = 1
    def make_frame(t):
        object_img = cv2.imread(object_path)
        img = clip.get_frame(t).astype(object_img.dtype)
        # object_img = cv2.resize(object_img, (int(clip.w/2), int(clip.h/2)))
        img = helpers.common.add_as_transparent_image(img, object_img)
        height, width, c = img.shape
        t = int(t*speed)*multiplier
        l = img[:, :(t % width)]
        r = img[:, (t % width):]

        img1 = np.hstack((r, l))
        return img1
    
    return make_frame

def get_clip(d=20):
    clip = mp.ColorClip(size=(270, 480), color=(100, 100, 100))
    clip = mp.VideoClip(make_moving_object_frame(clip, direction='left'),duration=d)
    clip = clip.fx(vfx.mask_color, color=(0,0,0))
    return clip

def preview_video():
    clip=get_clip()
    clip.preview(fps=30)

def main():
    # animate1()
    # plot()
    preview_video()
