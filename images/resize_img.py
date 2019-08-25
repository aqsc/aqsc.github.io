import cv2
import argparse

if __name__=='__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("-i", "--image", help="input image")
    args = parse.parse_args()
    img_file = args.image
    img = cv2.imread(img_file)
    img_rz = cv2.resize(img, (960, 480))
    cv2.imwrite(img_file, img_rz)