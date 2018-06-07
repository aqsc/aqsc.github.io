# http://aqsc.github.io/
## active imgpath 
## active annotation path 

#!/usr/bin/env python
import os,sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import TextBox
import matplotlib.gridspec as gridspec
from PIL import  Image
import argparse
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

import xml.etree.ElementTree as ET
from PIL import Image, ImageStat
import xml.dom.minidom as xdm
 
def parse_args():
    parser = argparse.ArgumentParser(description=\
    "Load and Save lable GUI\
    Hot key:\
        'r' read lable file if exist\
        'w' right bboxes on the image to lable file\
        'q' write lable file and quit, and to load next image\
        'f' full screen toggle key"\
    )
    
    parser.add_argument('--path',      dest='root_path', help='directory include images and lables', default='.\\', type=str)
    parser.add_argument('--dataset',   dest='dataset_name', help='dataset name input', default=None)#, type=str)
    parser.add_argument('--worklist',  dest='worklist_name', help='worklist name input', default=None)#, type=str)
    parser.add_argument('--bbmode',    dest='bbox_mode', help='area: (leftx,topy,w,h), point: (leftx,topy,buttomx,bottomy)', default='point', type=str)
    parser.add_argument('--writemode', dest='write_mode',help="append: never delete bbox in file, only append, override: save bbox on screen to file when typing 's'", default='append', type=str)
    parser.add_argument('--search_mode', dest='search_mode',help="jpg: priority to search by image path, xml:priority to search by xml path", default='jpg', type=str)
    args = parser.parse_args()

    if not os.path.exists(args.root_path):
       parser.print_help()
       sys.exit(1)

    return args


class Box(QMainWindow):
    def __init__(self, fig, ax, img, filename, size, args):
        super().__init__()
        self._fig = fig
        self._ax = ax
        self._img = img
        self._state = 'idel'
        self._pressed_point = []
        self._box = [] #[patch.rectangel, [txt]]
        self._boxlist = [] #[patch.rectangel, [txt]]
        self._box_index = 0
        self._filename = filename
        
        self._size = size
        self._bbox_mode = args.bbox_mode
        self._write_mode = args.write_mode
        self._anno_type = filename.split('.')[-1]
        #print("============\n", self._anno_type, "\n============\n")
        fig.canvas.mpl_connect('button_press_event',self._press)
        fig.canvas.mpl_connect('button_release_event',self._release)
        fig.canvas.mpl_connect('motion_notify_event',self._motion)
        fig.canvas.mpl_connect('key_press_event', self._load)
        fig.canvas.mpl_connect('key_press_event', self._save)
        fig.canvas.mpl_connect('key_press_event', self._hide)
        fig.canvas.mpl_connect('button_press_event', self._select_bbox)
        if 'txt' == self._anno_type:
            self._load_labels()
        else:
            self._load_labels_xml()

    def _legalCheck(self, x):
        if self._bbox_mode == 'point':
            if x[0] >= x[2] or x[1] >= x[3]:
                print('bbox point [2]>=[0] or x[3]>=[1] in {:s}'.format(self._filename))
                return False

            if x[0] >= self._size[0] or x[1] >= self._size[1] or x[2] >= self._size[0] or x[3] >=self._size[1]:
                print('bbox point [0]or[1]or[2]or[3] is out of image {:s}'.format(self._filename))
                return False
        else:
            if x[0]+x[2] > self._size[0] or x[1]+x[3] > self._size[1]:
                print('bbox is out of image {:s}'.format(self._filename))
                return False
        return True

    def _isRepeated(self, x, box_list):
        if 'point' == self._bbox_mode:
            width = x[2] - x[0]
            height = x[3] - x[1]
        else:
            width = x[2]
            height = x[3]

        for box in box_list:
            if int(box[0].get_x()) == x[0] and int(box[0].get_y()) == x[1] and int(box[0].get_width()) == width and int(box[0].get_height()) == height:
                return True
        return False
    
    def _refresh_bbox_ui(self, box, x): #x [leftx,topy]
        x = [int(box[0].get_x()),int(box[0].get_y())]
        x = list(map(str,x))
        txt = " ".join(x) +" " + " ".join(box[1])
        ax.text(box[0].get_x() - 8,box[0].get_y() - 8, txt, fontsize=11, color='r')

        self._ax.add_patch(box[0])

    
    def read_xml(self, filename):
        annotation_file = filename
        tree = ET.parse(annotation_file)
        objs = tree.findall('object')
        size = tree.find('size')
        width = int(size.find('width').text.strip())
        height = int(size.find('height').text.strip())
        num_objs = len(objs)
        box_lists = []
        illegal = 0
        for o in objs:
            cls = o.find('name').text.lower().strip()
            name = cls
            bbox = o.find('bndbox')
            x1 = int(bbox.find('xmin').text)
            y1 = int(bbox.find('ymin').text)
            if 'point'==self._bbox_mode:
                x2 = int(bbox.find('xmax').text)
                y2 = int(bbox.find('ymax').text)
                w = x2 - x1
                h = y2 - y1
            else:
                w = int(bbox.find('width').text)
                h = int(bbox.find('height').text)
            if x1 > width or x2 > width or y1 > height or y2 > height:
                print ('{:s} obj {:s} bbox {:d} {:d} {:d} {:d} x1 > width or x2 > width or y1 > height or y2 > height'.format(annotation_file, name, x1, y1, x2, y2))
                illegal += 1
                continue
            if w <= 1 or h <= 1:
                print ('{:s} obj {:s} bbox {:d} {:d} {:d} {:d} w<=1 or h<=1'.format(annotation_file, name, x1, y1, x2, y2))
                illegal += 1
                continue
            if w >= width or h >= height:
                print ('{:s} obj {:s} bbox {:d} {:d} {:d} {:d} {:d} {:d} w>widht or h>height'.format(annotation_file, name, x1, y1, x2, y2, width, height))
                illegal += 1
                continue

            box_lists.append([str(x1), str(y1), str(x2), str(y2)])
        return box_lists

    def write_xml(self, filename, boxes):
        root = ET.Element('annotation')
        resolution = ET.SubElement(root, 'size')
        width = ET.SubElement(resolution, 'width')
        height = ET.SubElement(resolution, 'height')
        depth = ET.SubElement(resolution, 'depth')
        width.text = str(self._size[0])
        height.text = str(self._size[1])
        depth.text = str(3)
        for box in boxes:
            x = [int(box[0].get_x()), int(box[0].get_y()),0,0]
            w = int(box[0].get_width())
            h = int(box[0].get_height())
            x[2] = x[0] + w
            x[3] = x[1] + h 

            xmin_value = x[0]
            ymin_value = x[1]
            
            obj = ET.SubElement(root, 'object')
            object = ET.SubElement(obj, 'name')
            object.text = 'pedestrian' #plate
            bbox = ET.SubElement(obj, 'bndbox')
            xmin = ET.SubElement(bbox, 'xmin')
            xmin.text = str(xmin_value)
            ymin = ET.SubElement(bbox, 'ymin')
            ymin.text = str(ymin_value)
    
            if 'point' == self._bbox_mode:
                xmax_value = x[2]
                ymax_value = x[3]
                xmax = ET.SubElement(bbox, 'xmax')
                xmax.text = str(xmax_value)
                ymax = ET.SubElement(bbox, 'ymax')
                ymax.text = str(ymax_value)
            else:
                width = ET.SubElement(bbox, 'width')
                width.text = str(w)
                height = ET.SubElement(bbox, 'height')
                height.text = str(h)
    
        xmls = xdm.parseString(ET.tostring(root, 'utf-8'))
        pretty_xml_as_string = xmls.toprettyxml()
        annoXML = filename
        with open(annoXML, 'wb+') as f:
            print(pretty_xml_as_string.encode('utf-8'))
            f.write(pretty_xml_as_string.encode('utf-8'))

    def _load_labels(self):
        if os.path.isfile(self._filename) :
            f = open(self._filename, 'r')
            lines = f.readlines()
            line = [x.strip() for x in lines]
            linelist = [x.split() for x in line]
            for x in linelist:
                txt = x[4:]
                x = list(map(int,x[0:4]))
                if not self._legalCheck(x):
                    return 1
                #we need to take care when typing 'r' sevral times
                if not self._isRepeated(x, self._boxlist):
                    if 'point' == self._bbox_mode:
                        width = x[2] - x[0]
                        height = x[3] - x[1]
                    else:
                        width = x[2]
                        height = x[3]
                    box = [patches.Rectangle((x[0],x[1]), width, height, fill=False, color='r'), txt]
                    self._boxlist.append(box)
                    self._refresh_bbox_ui(self._boxlist[-1],x)
            self._fig.canvas.draw()
            f.close()

    def _load_labels_xml(self):
        if os.path.isfile(self._filename):
            box_list = self.read_xml(self._filename)
            for x in box_list:
                x = list(map(int, x))
                if not self._legalCheck(x):
                    return 1
                if not self._isRepeated(x, self._boxlist):
                    if 'point' == self._bbox_mode:
                        width = x[2] - x[0]
                        height = x[3] - x[1]
                    else:
                        width = x[2]
                        height = x[3]
                    box = [patches.Rectangle((x[0],x[1]), width, height, fill=False, color='r'), []]
                    self._boxlist.append(box)
                    self._refresh_bbox_ui(self._boxlist[-1],x)
            self._fig.canvas.draw()


    def _save_labels(self):
        if ('append' == self._write_mode):
            self._load_labels()

        f = open(self._filename, 'w')
        for box in self._boxlist:
            x = [int(box[0].get_x()),int(box[0].get_y()),0,0]
            w = int(box[0].get_width())
            h = int(box[0].get_height())
            x[2] = x[0] + w
            x[3] = x[1] + h 
            if w != 0 and h != 0:
                if 'point' == self._bbox_mode:
                    f.write('{:d} {:d} {:d} {:d} {:s}\n'.format(x[0],x[1],x[2],x[3]," ".join(box[1])))
                else:
                    f.write('{:d} {:d} {:d} {:d} {:s}\n'.format(x[0],x[1],w,h, " ".join(box[1])))

    def _save_labels_xml(self):
        if 'append' == self._write_mode:
            self._load_labels_xml()    
        annotation_file = self._filename
        bbox_list = self._boxlist
        print("\n=======bbox_list=====\n", bbox_list, "\n===============\n\n")
        self.write_xml(annotation_file, bbox_list) 
        

    def _load(self, event):
        if event.key == 'r':
            if 'txt' == self._anno_type:
                self._load_labels()
            else:
                self._load_labels_xml()


    def _save(self, event):
        if event.key == 'w':
            if 'txt' == self._anno_type:
                self._save_labels()
            else:
                self._save_labels_xml()
            
    def _press(self, event):
        if event.xdata != None and event.ydata != None:
            self._state = 'mouse_pressed'
            self._pressed_point = [event.xdata,event.ydata]
            self._box = [patches.Rectangle((int(self._pressed_point[0]),int(self._pressed_point[1])), 0, 0, fill=False, color='r'), []]
    def _release(self, event):
        if event.xdata != None and event.ydata != None:
            self._state = 'mouse_released'
            if self._pressed_point != [event.xdata,event.ydata]:
                w = int(abs(self._pressed_point[0] - event.xdata))
                h = int(abs(self._pressed_point[1] - event.ydata))
                self._box[0].set_width(w)
                self._box[0].set_height(h)
                self._boxlist.append(self._box)

    def _motion(self, event):
        if self._state == 'mouse_pressed':
            if event.xdata != None and event.ydata != None:
                if self._pressed_point != [event.xdata,event.ydata]:
                    w = int(abs(self._pressed_point[0] - event.xdata))
                    h = int(abs(self._pressed_point[1] - event.ydata))
                    self._box[0].set_width(w)
                    self._box[0].set_height(h)
                    self._refresh_bbox_ui(self._box, self._pressed_point)
                    self._fig.canvas.draw()

    def _mouse_is_in_box(self, box, point):
        b = [box[0].get_x(), box[0].get_y(), 0, 0]
        b[2] = b[0] + box[0].get_width()
        b[3] = b[1] + box[0].get_height()
        if point[0] >= b[0] and point[0] <= b[2] and point[1] >= b[1] and point[1] <= b[3]:
            return True
        else:
            return False

    def _refresh_all(self): #very slow because of imshow
        self._ax.cla()
        self._ax.imshow(self._img)
        for box in self._boxlist:
            x = [int(box[0].get_x()), int(box[0].get_y()), int(box[0].get_width()), int(box[0].get_height())]
            self._refresh_bbox_ui(box, x)
        self._fig.canvas.draw()

    def _remove_pointed_bbox(self, point):
        if len(self._boxlist) > 0:
            for box in self._boxlist:
                if self._mouse_is_in_box(box, point):
                    box[0].remove()
                    self._boxlist.remove(box)
                    break
            else:
                self._boxlist[-1][0].remove()
                self._boxlist.pop()
            
    def _hide(self, event):
        if event.key == 'escape' and event.xdata != None and event.ydata != None:
            self._remove_pointed_bbox([event.xdata,event.ydata])
            self._refresh_all()

    def _select_bbox(self, event):
        if event.dblclick and event.xdata != None and event.ydata != None:
            if len(self._boxlist) > 0:
                for i in range(len(self._boxlist)):
                    if self._mouse_is_in_box(self._boxlist[i], [event.xdata,event.ydata]):
                        self._box_index = i
                        self._input_window()

    def _input_window(self):
        box = self._boxlist[self._box_index][0]
        txtlist = self._boxlist[self._box_index][1]
        self.setWindowTitle('{:d} {:d} {:d} {:d} {:s}'.format(box.get_x(),box.get_y(),box.get_width(),box.get_height(),' '.join(txtlist)))
        self.setGeometry(400, 400, 400, 50)
        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.insert(' '.join(txtlist))
        self.textbox.move(10, 10)
        self.textbox.resize(200, 30)
        # Create a button in the window
        self.button = QPushButton('save', self)
        self.button.move(220,10)
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()

    @pyqtSlot()
    def on_click(self):
        self._boxlist[self._box_index][1] = self.textbox.text().split(' ')
        if 'txt' == self._anno_type:
            self._save_labels()
        else:
            self._save_labels_xml()
        #self._save_labels()
        self._refresh_all()

# xml and img not in the same folder, stored like VOC
        # python label.py --path /data --dataset face_body --worklist pedestrian_train
# xml and img are all in the same folder
        # python label.py --path /data/face_body_2

def init_xml(annoXML_name):
    root = ET.Element('annotation')
    resolution = ET.SubElement(root, 'size')
    width = ET.SubElement(resolution, 'width')
    height = ET.SubElement(resolution, 'height')
    depth = ET.SubElement(resolution, 'depth')
    width.text = str(1080)
    height.text = str(720)
    depth.text = str(3)
    
    xmls = xdm.parseString(ET.tostring(root, 'utf-8'))
    pretty_xml_as_string = xmls.toprettyxml()
    
    with open(annoXML_name, 'wb+') as f:
        print(pretty_xml_as_string.encode('utf-8'))
        f.write(pretty_xml_as_string.encode('utf-8'))

if __name__ == '__main__':
    args = parse_args()
    if (args.dataset_name != None) and (args.worklist_name!=None): 
       	path = args.root_path  # input path is the xml_path                
        dataset_name = args.dataset_name
        worklist_name= args.worklist_name
        xml_path = os.path.join(path, 'datasets', dataset_name, 'Annotations', worklist_name)
        img_path = os.path.join(path, 'datasets', dataset_name, "Images")
        
        wl = open(os.path.join(path, 'list', dataset_name, worklist_name + '.txt'))
        worklist = wl.readlines()
        if args.search_mode =='jpg':
            imgname_list = []
            for f in worklist:
                if os.path.isfile(img_path+'/'+f.split()[0] + '.jpg'):
                    imgname = f.split()[0] + '.jpg'
                elif os.path.isfile(img_path+'/'+f.split()[0] + '.JPG'):
                    imgname = f.split()[0] + '.JPG'
                elif os.path.isfile(img_path+'/'+f.split()[0] + '.png'):
                    imgname = f.split()[0] + '.png'
                elif os.path.isfile(img_path+'/'+f.split()[0] + '.PNG'):
                    imgname = f.split()[0] + '.PNG'
                imgname_list.append(imgname)
        else:
            xmlname_list = [f.split()[0] + '.xml' for f in worklist if os.path.isfile(xml_path+'/'+f.split()[0] + '.xml')]
    else:
        img_path = args.root_path+'/Images'
        xml_path = args.root_path+'/Annotations'
        if args.search_mode =='jpg':
            imgfiles = os.listdir(img_path)
            imgfiles.sort()
            imgname_list = [f for f in imgfiles if os.path.isfile(img_path+'/'+f)  and \
                    ((f.split('.')[-1]=='jpg')|(f.split('.')[-1]=='JPG')|(f.split('.')[-1]=='png')|(f.split('.')[-1]=='PNG'))]
        else:
            xml_files = os.listdir(xml_path)
            xml_files.sort()
            xmlname_list = [f for f in xml_files if os.path.isfile(xml_path+'/'+f) and (f.split('.')[-1]=='xml')]
        
    if  args.search_mode == 'xml':
        assert 0 != len(xmlname_list), "There isn't any annatated xml in {}".format(xml_path)
        for f in range(len(xmlname_list)):
            f = f + 0       # debug
            print("process the " + str(f) + " xml.\n")
            xml_file = xmlname_list[f]
            pure_name = xml_file.split('.')[0]
            img_file = pure_name+'.jpg'
            assert os.path.isfile(img_path + '/' + img_file), "There isn't {} in {}".format(img_file, img_path)
            img = Image.open(img_path + '/' + img_file)
            img_ratio = float(img.size[0])/img.size[1]
            fig = plt.figure(figsize=(12, int(12.0/img_ratio)))
            ax = fig.add_subplot(111)
            ax.imshow(img)
            plt.suptitle(img_file)
            fig.tight_layout()
            box = Box(fig, ax, img, xml_path+ '/' + xml_file, img.size, args)
            plt.show()
    elif args.search_mode == 'jpg':
        assert 0 != len(imgname_list), "There isn't any jpg in {}".format(jpg_path)
        for f in range(len(imgname_list)):
            f = f + 0       # debug
            print("process the " + str(f) + " image.\n")
            img_file = imgname_list[f]
            pure_name = img_file.split('.')[0]
            xml_file = pure_name+'.xml'
            if not os.path.isfile(xml_path+'/'+xml_file):
                init_xml(xml_path+'/'+xml_file)
            img = Image.open(img_path + '/' + img_file)
            img_ratio = float(img.size[0])/img.size[1]
            fig = plt.figure(figsize=(12, int(12.0/img_ratio)))
            ax = fig.add_subplot(111)
            ax.imshow(img)
            
            plt.suptitle(img_file)
            fig.tight_layout()
            
            box = Box(fig, ax, img, xml_path+ '/' + xml_file, img.size, args)
            plt.show()



    #for f in imgfiles:
    #    img = Image.open(f)
    #    fig = plt.figure()
    #    ax = fig.add_subplot(111)
    #    ax.imshow(img)
    #    
    #    plt.suptitle(f)
    #    fig.tight_layout()
    #    xml_file = os.path.join(path, Annotations)
    #    box = Box(fig, ax, img, f[:f.rfind('.')]+'.txt', img.size, args)
    #    plt.show()
