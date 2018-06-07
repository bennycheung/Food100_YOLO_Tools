# food100_generate_bbox_file.py
#
# Read each food100 class image directory 'bb_info.txt' and create individual bbox files.
#
# This script creates 2 bounding box files for each food image:
# (1) The bounding box file that is saved along with the image in the same directory,
#     this allow to use bounding box editing tool. When the image re-edit,
#     it remembers the previous edited bounding boxes.
# (2) The bounding box file that is saved in 'labels' directory,
#     parallel to the image file and using darknet expected bbox format.
#     This allows darknet YOLO training with the expected bbox format.
#

import os
from PIL import Image

# modify the directories and class file to fit
datapath = 'images'
labelpath = 'labels'
classfilename = 'food100.names'

def convert_yolo_bbox(img_size, box):
    # img_bbox file is [0:img] [1:left X] [2:bottom Y] [3:right X] [4:top Y]
    dw = 1./img_size[0]
    dh = 1./img_size[1]
    x = (int(box[1]) + int(box[3]))/2.0
    y = (int(box[2]) + int(box[4]))/2.0
    w = abs(int(box[3]) - int(box[1]))
    h = abs(int(box[4]) - int(box[2]))
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    # Yolo bbox is center x, y and width, height
    return (x,y,w,h)

def generate_bbox_file(datapath, labelpath, classid, classname):
    dataDir = os.path.join(datapath, str(classid))
    labelDir = os.path.join(labelpath, str(classid))
    bb_filename = os.path.join(dataDir, 'bb_info.txt')
    if not os.path.exists(labelDir):
        os.makedirs(labelDir)
    with open(bb_filename) as fp:
        for line in fp.readlines():
            # img_bbox file is [0:img] [1:left X] [2:bottom Y] [3:right X] [4:top Y]
            img_bbox = line.strip('\n').split(' ')
            if img_bbox[0] != 'img':
                img_bbox_filename = os.path.join(dataDir, img_bbox[0]+'.txt')
                with open(img_bbox_filename, 'w') as f:
                    # [number of bbox]
                    # [left X] [top Y] [right X] [bottom Y] [class name]
                    f.write('1\n')
                    f.write('%s %s %s %s %s\n' %(img_bbox[1], img_bbox[4], img_bbox[3], img_bbox[2], classname))
                    f.close()

                image_filename = os.path.join(dataDir, img_bbox[0]+'.jpg')
                yolo_label_filename = os.path.join(labelDir, img_bbox[0]+'.txt')
                with open(yolo_label_filename, 'w') as f:
                    img = Image.open(image_filename)
                    yolo_bbox = convert_yolo_bbox(img.size, img_bbox)
                    if (yolo_bbox[2] > 1) or (yolo_bbox[3] > 1):
                        print("image %s bbox is " %(image_filename) + ' '.join(map(str, yolo_bbox)))
                    f.write(str(classid-1) + ' ' + ' '.join(map(str, yolo_bbox)) + '\n')
                    img.close()
                    f.close()
        fp.close()

classid = 0
classid2name = {}
if os.path.exists(classfilename):
    with open(classfilename) as cf:
        for line in cf.readlines():
            classname = line.strip('\n')
            classid = classid + 1
            classid2name[classid] = classname

for id in classid2name.keys():
    print("generating %d %s" %(id, classid2name[id]))
    generate_bbox_file(datapath, labelpath, id, classid2name[id])

