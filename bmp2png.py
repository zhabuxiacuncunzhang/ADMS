import os
import sys
from PIL import Image

def bmp2png(file_dir):
    for root, dirs, files in os.walk(file_dir):  # get all files
        for idx,file in enumerate(files):
            if os.path.splitext(file)[1] == '.bmp':   # important
                im = Image.open(os.path.join(root, file))  # open img file
                im = im.convert("RGB")
                newname = file[:file.rindex('.')] + '.png'  # new name for png file
                im.save(os.path.join(root, newname))  # to png



def main(argv):
    print("*****************************************")
    print("*             bmp to png                *")
    print("*            Xuesong Zhang              *")
    print("*             2023.03.01                *")
    print("*****************************************")
    if (len(argv) < 1 or len(argv) > 1):
        print("usage:")
        print("    bmp2png.py <bmp_path>")
        print("        bmp_path  path containing bmp files")
    else:
        bmp2png(argv[0])

if __name__ == '__main__':
    main(sys.argv[1:])
