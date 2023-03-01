'''
Descripttion: picAutoDetect
version: 
Author: Xuesong_Zhang
Date: 2023-02-28 21:16:34
LastEditors: Xuesong_Zhang
LastEditTime: 2023-03-01 20:21:51
'''
import os
import sys
import numpy as np
import skimage.io
from skimage.measure import find_contours
from mrcnn.config import Config
from mrcnn import utils
from mrcnn import visualize
import mrcnn.model as modellib

try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr


def load_model():
    print("Load Model Parameter")
    ROOT_DIR = os.getcwd()
    MODEL_DIR = os.path.join(ROOT_DIR, "parameter")
    # parameter file in parameter folder
    COCO_MODEL_PATH = os.path.join(MODEL_DIR, "mask_rcnn_shapes_0003.h5")

    if not os.path.exists(COCO_MODEL_PATH):
        print("Can't find the parameter file!")
        exit()

    class ShapesConfig(Config):
        """Configuration for training on the toy shapes dataset.
        Derives from the base Config class and overrides values specific
        to the toy shapes dataset.
        """
        # Give the configuration a recognizable name
        NAME = "shapes"

        # Train on 1 GPU and 8 images per GPU. We can put multiple images on each
        # GPU because the images are small. Batch size is 8 (GPUs * images/GPU).
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1

        # Number of classes (including background)
        NUM_CLASSES = 1 + 1  # background + 3 shapes

        # Use small images for faster training. Set the limits of the small side
        # the large side, and that determines the image shape.
        IMAGE_MIN_DIM = 768
        IMAGE_MAX_DIM = 832

        # Use smaller anchors because our image and objects are small
        RPN_ANCHOR_SCALES = (8 * 6, 16 * 6, 32 * 6, 64 * 6,
                             128 * 6)  # anchor side in pixels

        # Reduce training ROIs per image because the images are small and have
        # few objects. Aim to allow ROI sampling to pick 33% positive ROIs.
        TRAIN_ROIS_PER_IMAGE = 100

        # Use a small epoch since the data is simple
        STEPS_PER_EPOCH = 100

        # use small validation steps since the epoch is small
        VALIDATION_STEPS = 50

    class InferenceConfig(ShapesConfig):
        # Set batch size to 1 since we'll be running inference on
        # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1

    config = InferenceConfig()

    # Create model object in inference mode.
    global model
    model = modellib.MaskRCNN(
        mode="inference", model_dir=MODEL_DIR, config=config)

    # Load weights trained on MS-COCO
    model.load_weights(COCO_MODEL_PATH, by_name=True)

    class_names = ['_background_', 'Detected']


def picAutoDetect(image_path):
    if not os.path.exists(image_path):
        print("Can't find the image file!")
        exit()
    else:
        print("now processing is ", image_path)

    image = skimage.io.imread(image_path)
    results = model.detect([image], verbose=1)
    r = results[0]

    return r

    print("End!")


def pixelToLL(result, X_first, Y_first, X_step, Y_step, save_path, first_name):
    masks = result['masks']
    boxes = result['rois']
    class_ids = result['class_ids']
    scores = result['scores']
    # Number of instances
    N = boxes.shape[0]
    if not N:
        print("\n*** No instances to display *** \n")
    else:
        assert boxes.shape[0] == masks.shape[-1] == class_ids.shape[0]

    detect_num = 0
    for i in range(N):
        # Mask
        mask = masks[:, :, i]
        score = scores[i]
        # Mask Polygon
        # Pad to ensure proper polygons for masks that touch image edges.
        padded_mask = np.zeros(
            (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
        padded_mask[1:-1, 1:-1] = mask
        contours = find_contours(padded_mask, 0.5)

        for verts in contours:
            # Subtract the padding and flip (y, x) to (x, y)
            verts = np.fliplr(verts) - 1
            resultLL = np.zeros_like(verts)
            # pixel to LonLat
            resultLL[:, 0] = X_first+verts[:, 0]*X_step
            resultLL[:, 1] = Y_first+verts[:, 1]*Y_step

            # save to file
            np.savetxt(save_path+'/'+first_name+'_'+str(detect_num)+'_'+str(score)+'.txt',
                       resultLL, fmt="%.8f", delimiter=" ")
            # save to shp
            save_shp(resultLL, save_path+'/'+first_name+'_' +
                     str(detect_num)+'_'+str(score)+'.shp')

            detect_num = detect_num+1


def save_shp(result, filename):
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")  # 为了使属性表字段支持中文
    ogr.RegisterAll()  # 注册所有的驱动
    strDriverName = "ESRI Shapefile"  # 创建数据，这里创建ESRI的shp文件
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("%s driver failed\n", strDriverName)

    oDS = oDriver.CreateDataSource(filename)  # 创建数据源
    if oDS == None:
        print("open %s failed", filename)

    srs = osr.SpatialReference()  # 创建空间参考
    srs.ImportFromEPSG(4326)  # 定义地理坐标系WGS1984
    papszLCO = []
    # 创建图层，创建一个多边形图层,"Polygon"->属性表名
    oLayer = oDS.CreateLayer("Polygon", srs, ogr.wkbPolygon, papszLCO)
    if oLayer == None:
        print("Layer creation failed\n")

    '''下面添加矢量数据，属性表数据、矢量数据坐标'''
    oFieldID = ogr.FieldDefn("FieldID", ogr.OFTInteger)  # 创建一个叫FieldID的整型属性
    oLayer.CreateField(oFieldID, 1)

    oFieldName = ogr.FieldDefn(
        "FieldName", ogr.OFTString)  # 创建一个叫FieldName的字符型属性
    oFieldName.SetWidth(100)  # 定义字符长度为100
    oLayer.CreateField(oFieldName, 1)

    oDefn = oLayer.GetLayerDefn()  # 定义要素

    # 创建单个面
    oFeatureTriangle = ogr.Feature(oDefn)
    oFeatureTriangle.SetField(0, 0)  # 第一个参数表示第几个字段，第二个参数表示字段的值
    oFeatureTriangle.SetField(1, "Detected mining")
    ring = ogr.Geometry(ogr.wkbLinearRing)  # 构建几何类型:线
    for i in result:
        ring.AddPoint(i[0], i[1])
    yard = ogr.Geometry(ogr.wkbPolygon)  # 构建几何类型:多边形
    yard.AddGeometry(ring)
    yard.CloseRings()

    geomTriangle = ogr.CreateGeometryFromWkt(str(yard))  # 将封闭后的多边形集添加到属性表
    oFeatureTriangle.SetGeometry(geomTriangle)
    oLayer.CreateFeature(oFeatureTriangle)


def fileAutoDetect(pic_file, pic_path, out_path):
    if not os.path.exists(pic_file):
        print("Can't find the file!")
        exit()
    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    load_model()
    f = open(pic_file, 'r')
    for lines in f:
        ls = lines.strip('\n').split(' ')
        filename = ls[0].split('/')[-1]
        filename = filename[:filename.rindex('.')]
        contours = picAutoDetect(pic_path+"/"+ls[0])
        pixelToLL(contours, float(ls[1]), float(ls[2]), float(
            ls[3]), float(ls[4]), out_path, filename)


def main(argv):
    print("*****************************************")
    print("*          pictures auto detect         *")
    print("*        Xuesong Zhang & Kelu He        *")
    print("*             2023.03.01                *")
    print("*****************************************")
    if (len(argv) < 3 or len(argv) > 3):
        print("usage:")
        print("    picAutoDetect.py <pic_tab> <pic_path> <result_path>")
        print("        pic_tab       four cols for picture_name(without path) left_top_lon left_top_lat lon_step lat_step")
        print("        pic_path      picture files path")
        print("        result_path   result path")
    else:
        fileAutoDetect(argv[0], argv[1], argv[2])


if __name__ == '__main__':
    main(sys.argv[1:])
