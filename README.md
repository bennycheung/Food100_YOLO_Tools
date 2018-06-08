This is the set of tools and configurations used by the YOLO Real-Time Food Detection article at <http://bennycheung.github.io/yolo-for-real-time-food-detection>

## Food100 YOLO Training Tools
The following instructions concentrated on describing YOLO v2 setup and training.
To get DarkNet YOLO training to work, we needs

* Object bounding box file for each image
* Class name file for all the category names
* Training dataset file for the list of training images
* Validating dataset file for the list of validating images
* Configuration file for YOLO neural network specification
* Data location file for finding all the data information

Here is my github <> of tools to help, check them out if in doubt! It also contains my configuration `.cfg`, class name `.names` and data location `.data` files described later.
They are designed or modified to working with DarkNet requirement for bounding box and training data.
* `food100_generate_bbox_file.py` - python script to take each of the Food100 class image directory `bb_info.txt` and create individual bbox files.
* `food100_split_for_yolo.py` - python script to split all Food100 class images into (1) `train.txt` training image list and (2) `test.txt` validating image list.
* `food100_tk_label_bbox.py` - python script using UI to help drawing bbox associating with the images.

### Object Bounding Box File
After downloaded and unpacked the Food100 dataset [UEC FOOD 100](http://foodcam.mobi/dataset100.html),
it requires post processing to make bounding box that fit into DarkNet's YOLO training requirements.

The Food100 classes are like,

| food_id | name |
|----|------|
| 1	| rice
| 2	| eels_on_rice
| 3	| pilaf
| 4	| chicken-n-egg_on_rice
| 5	| pork_cutlet_on_rice
| 6	| beef_curry
| 7	| sushi
| ... | up to 100 classes

#### Bounding Box Class Number
DarkNet YOLO (both v2 and v3) expected the class number is 0 based, that the food_id-1 to get the class number

```
<object-class-id> <center-X> <center-Y> <width> <height>
```

> Originally, I forgot to subtract 1 for the <object-class-id>; that's make me think the method is not working and almost gives up! After re-align to 0 based <object-class-id>, the detection shows correct results.

#### Bounding Box Description File
DarkNet YOLO expected a bounding box `.txt`-file for each `.jpg`-image-file - in the same directory and with the same name, but with `.txt`-extension, and put to file: object number and object coordinates on this image.

If we named our food100 image directory as `images`, then DarkNet will automatically look for the corresponding `.txt` in `labels` directory. For example, `images/1/2.jpg` will look for corresponding label in `labels/1/2.txt` file. I like this approach because we can keep the editing bbox in `images/1/2.txt`, while the `labels/1/2.txt` is the bbox format required for YOLO training.

#### Bounding Box Coordinate in Image
For each food class directory, there is a `bb_info.txt` that contains all the bbox for every image files. The original bbox is specified as,

```
<image-number> <top-left-X> <top-left-Y> <bottom-right-X> <bottom-right-Y>
```

However, YOLO expected each `.jpg`-image-file has a corresponding bbox description `.txt`-extension file. The bbox description file is specified as,

```
<object-class-id> <center-X> <center-Y> <width> <height>
```

* <object-class-id> - integer number of object from 0 to (food_id-1)
* <center-X> <center-Y> <width> <height> - float values relative to width and height of image, it can be equal from (0.0 to 1.0]
  * for example: <x> = <absolute_x> / <image_width> or <height> = <absolute_height> / <image_height>
  * attention: <center-X> <center-Y> - are center of bounding box (are not top-left corner)


### Data Location File
The data file to tell where to find the training and validation paths, `food100.data`

```
classes = 100
train = /Users/bcheung/dev/ML/darknet/data/food100/train.txt
valid = /Users/bcheung/dev/ML/darknet/data/food100/test.txt
names = /Users/bcheung/dev/ML/darknet/data/food100/food100.names
backup = backup
```

* classes = 100 is the number of classes, should equal to line counts of class name file
* train = <path> is the file list of all training images, one image per line
* valid = <path> is the file list of all validating images, one image per line
* names = <path> is the file that list class names
* backup = <path> is where the intermediate `.weights` and final `.weights` files will be written

Obviously, change the data <path> to your specific data locations.

### Traning Dataset File
The `train.txt` file list of all training images, one image per line. For example,

```
/Users/bcheung/dev/ML/darknet/data/food100/images/61/6164.jpg
/Users/bcheung/dev/ML/darknet/data/food100/images/61/6170.jpg
/Users/bcheung/dev/ML/darknet/data/food100/images/61/6158.jpg
...
```

There should be no image coming from the validating dataset.

### Validating Dataset File
The `test.txt` file list of all validating images, one image per line. For example,

```
/Users/bcheung/dev/ML/darknet/data/food100/images/61/6990.jpg
/Users/bcheung/dev/ML/darknet/data/food100/images/61/6149.jpg
/Users/bcheung/dev/ML/darknet/data/food100/images/61/6099.jpg
...
```

There should be no image coming from the training dataset.

### Class Name File
The class names specified in, `food100.names`
Subsequently, the class id is 0-based, i.e. `rice` is class `0`.
There is no class-id, just names.

```
rice
eels-on-rice
pilaf
chicken-n-egg-on-rice
pork-cutlet-on rice
beef-curry
sushi
...
```

### Configuration File
We need to create a configuration file `yolov2-food100.cfg`.
> You can copy darknet `cfg/yolov2-voc.cfg` and make modifications

```
[net]
# Testing
# batch=1
# subdivisions=1
# Training
batch=64
subdivisions=8
...
```

The meaning of batch and subdivisions is how many mini batches
you split your batch in.

* batch=64 -> loading 64 images for this "iteration".
* subdivision=8 -> Split batch into 8 "mini-batches" so 64/8 = 8 images per "minibatch" and this get sent to the GPU for process.

That will be repeated 8 times until the batch is completed and a new itereation will start with 64 new images. When batching you are averaging over more images the intend is not only to speed up the training process but also to generalise the training more.
If your GPU have enough memory you can reduce the subdivision to load more images into the gpu to process at the same time.

Further editing to the configuration file `classes` and `filters` specifications,

```
# number of filters calculated by (#-of-classes + 5)*5
# e.g. (100 + 5)*5 = 525
edit to line 237: filters=525
edit to line 244: classes=100
```
