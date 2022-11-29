import cv2

def get_mask(img):
    mask = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)[1]
    return mask

def add_as_transparent_image(img1, img2):
    rows,cols,channels = img2.shape
    roi = img1[0:rows, 0:cols]
    # Now create a mask of logo and create its inverse mask also
    mask = get_mask(img2)
    mask_inv = cv2.bitwise_not(mask)
    # Now black-out the area of logo in ROI
    img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
    # Take only region of logo from logo image.
    img2_fg = cv2.bitwise_and(img2,img2,mask = mask)
    # Put logo in ROI and modify the main image
    dst = cv2.add(img1_bg,img2_fg)
    img1[0:rows, 0:cols ] = dst
    return img1

