<!--
 * @Descripttion: file content
 * @version: 
 * @Author: Xuesong_Zhang
 * @Date: 2023-03-01 20:16:42
 * @LastEditors: Xuesong_Zhang
 * @LastEditTime: 2023-03-04 20:03:02
-->
# ADMS
Automatic detection of mining subsidence

# Python files

1. bmp2png.py
   * Convert the color picture of the wrapped interferogram produced by GAMMA to png format

2. cutPic.py
   * Crops the png picture to 800*800 pixels

3. picAutoDetect.py
    * Automatic detection

4. multiSHP2one.py
   * Merge multiple SHP files into one SHP file

# Usage

1. InSAR Process
   * You can use GAMMA, SARscape, GMTSAR, ISCE, etc, InSAR process software to process SAR images to get interferometry images.
   * Interferometry images do not need to be unwrapped, ADMS identifies the wrapped stripes.
   * Plot all interferometry images as RGB color images in *.png format.
   * P.S. the file naming scheme is YYYYMMDD-YYYYMMDD.diff, please do not use <u>underscores</u>, as this will affect the processing later
2. bmp2png.py (Optional)
   * If you can only generate color images in RGBA \*.bmp format using software such as GAMMA, this script will provide conversion from RGBA \*.bmp format to RGB \*.png format.
   * Before starting this step, please place all the *.png images into one folder.
3. cutPic.py
   * For sufficient detection speed, all images will be cropped to a pixel size of 800*800.
   * In this step, a header file is necessary, which will provide the necessary coordinate information.
4. picAutoDetect.py
   * This step will detect all cropped images and generate the resulting \*.shp file and \*.txt file.
   * A \*.shp file and a corresponding \*.txt file will be generated for each detection result.
5. multiSHP2one.py (Optional)
   * In this step, all the *.shp files from the previous step will be merged into one shp file.
   * It can be easily imported into a PostgreSQL database.
