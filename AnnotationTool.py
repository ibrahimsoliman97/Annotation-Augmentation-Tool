
'''
Annotate a PCB image.
Ibrahim Soliman Mohamed, 4BENG, FKEKK, UTeM, Malaysia 
'''
import glob
import cv2
import numpy as np
from PyQt4 import QtGui, QtCore
import sys
import os.path

class Annot:

    def __init__(self, rect, classIndex=0):
        if rect is None:
            rect = ((0, 0), (0, 0), 0)
        self.rect = rect
        self.classIndex = classIndex

    def __repr__(self):
        return 'Annotation {} "{}"'.format(self.rect, self.classIndex)


def parse_annotation_file(path, h, w):
    lines = None
    with open(path) as f:
        lines = [l.strip().split() for l in f.readlines()]

    ret = []
    for l in lines:
        l = [x.strip() for x in l]
        if len(l) < 5:
            raise Exception('Failed to parse line "{}"'.format(l))

        rect = [float(s) for s in l[1:5]]
        angle = 0.0 if len(l) == 5 else float(l[5])
        ret.append(Annot(((rect[0]*w,rect[1]*h), (rect[2]*w,rect[3]*h), angle), l[0]))
    return ret


def write_annotation_file(data, to, h, w):
    with open(to, 'w') as f:
        for d in data:
            f.write('{:d} {:.6f} {:.6f} {:.6f} {:.6f} {:.2f}\n'.format(int(d.classIndex), (d.rect[0][0]/w), (d.rect[0][1]/h), (d.rect[1][0]/w), (d.rect[1][1]/h), d.rect[2]))

def write_annotation_file_90(data, to, h, w):
    with open(to, 'w') as f:
        for d in data:
            f.write('{:d} {:.6f} {:.6f} {:.6f} {:.6f} {:.2f}\n'.format(int(d.classIndex),((h-d.rect[0][1])/w), (d.rect[0][0]/h), (d.rect[1][0]/w), (d.rect[1][1]/h), (d.rect[2]+90.0)))

def write_annotation_file_180(data, to, h, w):
    with open(to, 'w') as f:
        for d in data:
            f.write('{:d} {:.6f} {:.6f} {:.6f} {:.6f} {:.2f}\n'.format(int(d.classIndex), ((w-d.rect[0][0])/w), ((h-d.rect[0][1])/h), (d.rect[1][0]/w), (d.rect[1][1]/h), d.rect[2]))

def write_annotation_file_270(data, to, h, w):
    with open(to, 'w') as f:
        for d in data:
            f.write('{:d} {:.6f} {:.6f} {:.6f} {:.6f} {:.2f}\n'.format(int(d.classIndex), (d.rect[0][1]/w), ((w-d.rect[0][0])/h), (d.rect[1][0]/w), (d.rect[1][1]/h), (d.rect[2]+90.0)))

def write_annotation_file_flip(data, to, h, w):
    with open(to, 'w') as f:
        for d in data:
            f.write('{:d} {:.6f} {:.6f} {:.6f} {:.6f} {:.2f}\n'.format(int(d.classIndex), ((w-d.rect[0][0])/w), (d.rect[0][1]/h), (d.rect[1][0]/w), (d.rect[1][1]/h), d.rect[2]))


def mat_to_qimage(mat):
    tmp = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
    h, w, bpc = tmp.shape
    return QtGui.QImage(tmp.data, w, h, bpc*w, QtGui.QImage.Format_RGB888)

def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

class MouseLabel(QtGui.QLabel):

    def __init__(self, parent):
        QtGui.QLabel.__init__(self, parent)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

    def updatePixmap(self, imagePixmap):
	    self.imagePix = imagePixmap	
  
    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.flag = False
        self.update()

    def mouseMoveEvent(self, event):
        self.setPixmap(self.imagePix)
        painter = QtGui.QPainter(self.pixmap())
        self.end = event.pos()
        painter.drawRect(QtCore.QRect(self.begin, self.end))
        painter.end()
        self.update()  
    
    def mouseReleaseEvent(self, event):
        self.emit(QtCore.SIGNAL('clicked(int, int, int, int, int)'), self.begin.x(), self.begin.y(), self.end.x(), self.end.y(), event.button())

class Window(QtGui.QWidget):

    def __init__(self):
 

        QtGui.QWidget.__init__(self)
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.setWindowTitle('Annotation & Augmentation Tool')
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.image_path = None
        iconsize = 0.047 *((screen.width()+ screen.height())/2)
        self.buttonopenFolder = QtGui.QToolButton()
        self.buttonopenFolder.setText('   Open Folder   ')
        self.buttonopenFolder.setIcon(QtGui.QIcon('./res/image.png'))
        self.buttonopenFolder.setIconSize(QtCore.QSize(int(iconsize),int(iconsize)))
        self.buttonopenFolder.setCheckable(True)
        self.buttonopenFolder.setFixedSize(int(1.8*iconsize),int(1.4*iconsize))
        self.buttonopenFolder.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.buttonopenFolder.clicked.connect(self.openFloder)

        self.nextImageButton = QtGui.QToolButton()
        self.nextImageButton.setText('Previous \nImage')
        self.nextImageButton.setIcon(QtGui.QIcon('./res/left.png'))
        self.nextImageButton.setIconSize(QtCore.QSize(int(0.5*iconsize),int(0.5*iconsize)))
        self.nextImageButton.setFixedSize(int(0.85*iconsize),int(1.4*iconsize))
        self.nextImageButton.setCheckable(True)
        self.nextImageButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.nextImageButton.clicked.connect(self.fetchPreviousImage)

        self.previousImageButton = QtGui.QToolButton()
        self.previousImageButton.setText('Next \nImage')
        self.previousImageButton.setIcon(QtGui.QIcon('./res/rightF.png'))
        self.previousImageButton.setIconSize(QtCore.QSize(int(0.5*iconsize),int(0.5*iconsize)))
        self.previousImageButton.setFixedSize(int(0.85*iconsize),int(1.4*iconsize))
        self.previousImageButton.setCheckable(True)
        self.previousImageButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.previousImageButton.clicked.connect(self.fetchNextImage)

        self.saveYoloFormat = QtGui.QToolButton()
        self.saveYoloFormat.setText('   Save Annot    ')
        self.saveYoloFormat.setIcon(QtGui.QIcon('./res/save.png'))
        self.saveYoloFormat.setIconSize(QtCore.QSize(int(iconsize),int(iconsize)))
        self.saveYoloFormat.setCheckable(True)
        self.saveYoloFormat.setFixedSize(int(1.8*iconsize),int(1.4*iconsize))
        self.saveYoloFormat.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.saveYoloFormat.clicked.connect(self.saveAnnotation)
        classlabel = QtGui.QLabel("Classes")
        self.classList = [line.rstrip('\n') for line in open('./classes.txt')]
	self.classIndx=0
        self.CBclass = QtGui.QComboBox()
        self.CBclass.addItems(self.classList)
        self.CBclass.currentIndexChanged.connect(self.selectionchange)
       
        l1 = QtGui.QLabel()
        l1.setText("Data Augmentation")

        self.rotateImage = QtGui.QToolButton()
        self.rotateImage.setText(' Roation ')
        self.rotateImage.setIcon(QtGui.QIcon('./res/rotate.png'))
        self.rotateImage.setIconSize(QtCore.QSize(int(iconsize),int(iconsize)))
        self.rotateImage.setCheckable(True)
        self.rotateImage.setFixedSize(int(1.8*iconsize),int(1.4*iconsize))
        self.rotateImage.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.rotateImage.clicked.connect(self.rotate3Image)

        self.flipping = QtGui.QToolButton()
        self.flipping.setText('  Flipping ')
        self.flipping.setIcon(QtGui.QIcon('./res/FLIP_F.png'))
        self.flipping.setIconSize(QtCore.QSize(int(iconsize),int(iconsize)))
        self.flipping.setCheckable(True)
        self.flipping.setFixedSize(int(1.8*iconsize),int(1.4*iconsize))
        self.flipping.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.flipping.clicked.connect(self.flippingImage)

        self.addnoise = QtGui.QToolButton()
        self.addnoise.setText('   Salt & Papper Noise   ')
        self.addnoise.setIcon(QtGui.QIcon('./res/noise.png'))
        self.addnoise.setIconSize(QtCore.QSize(int(iconsize),int(iconsize)))
        self.addnoise.setCheckable(True)
        self.addnoise.setFixedSize(int(1.8*iconsize),int(1.4*iconsize))
        self.addnoise.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.addnoise.clicked.connect(self.addnoiseImage)

        self.addBright = QtGui.QToolButton()
        self.addBright.setText('   Brightness   ')
        self.addBright.setIcon(QtGui.QIcon('./res/bright.png'))
        self.addBright.setIconSize(QtCore.QSize(int(iconsize),int(iconsize)))
        self.addBright.setCheckable(True)
        self.addBright.setFixedSize(int(1.8*iconsize),int(1.4*iconsize))
        self.addBright.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.addBright.clicked.connect(self.addBrightImage)

        utemlogo = QtGui.QLabel()
        pixmap = QtGui.QPixmap('./res/utem.png')
        utemlogo.setPixmap(pixmap.scaled(int(2*iconsize),int(1.5*iconsize),QtCore.Qt.KeepAspectRatio))
        fkekklogo = QtGui.QLabel()
        pixmap = QtGui.QPixmap('./res/fkekk.png')
        fkekklogo.setPixmap(pixmap.scaled(int(2*iconsize),int(1.5*iconsize),QtCore.Qt.KeepAspectRatio))

        ButtonLayout = QtGui.QVBoxLayout()
        ButtonLayout.setAlignment(QtCore.Qt.AlignCenter)
        ButtonLayout.addWidget(self.buttonopenFolder)
        hboxRL = QtGui.QHBoxLayout()
        hboxRL.addWidget(self.nextImageButton)
        hboxRL.addWidget(self.previousImageButton)
        ButtonLayout.addLayout(hboxRL)
        ButtonLayout.addWidget(self.saveYoloFormat)
        ButtonLayout.addWidget(classlabel)
        ButtonLayout.addWidget(self.CBclass)
        ButtonLayout.addStretch()
        ButtonLayout.addWidget(l1)
        ButtonLayout.addWidget(self.rotateImage)
        ButtonLayout.addWidget( self.flipping)
        ButtonLayout.addWidget(self.addnoise)
        ButtonLayout.addWidget(self.addBright)
        ButtonLayout.addStretch()
        ButtonLayout.addWidget(fkekklogo)
        ButtonLayout.addWidget(utemlogo)

        self.label_image = MouseLabel(self)
        self.scroll = QtGui.QScrollArea(self)
        self.scroll.setWidget(self.label_image)
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.scroll)
        hbox.addLayout(ButtonLayout)

        self.connect(self.label_image, QtCore.SIGNAL('clicked(int, int, int, int, int)'), self.point_selected)

    def openFloder(self):
        dlg = QtGui.QFileDialog(self)
        dlg.setFileMode(QtGui.QFileDialog.AnyFile)
        dlg.setFilter("Image files (*.jpg *.png *.jpeg)")
        dlg.show()
        if dlg.exec_():
            filenames = str(dlg.selectedFiles()[0])
            img = cv2.imread(filenames)
            annot_name = os.path.join(os.path.dirname(filenames), '{}.txt'.format(os.path.splitext(filenames)[0]))
            annot_data = []
            if os.path.isfile(annot_name):
                print('Loading existing annotation file')
                annot_data = parse_annotation_file(annot_name,img.shape[0],img.shape[1])
            self.newImage(filenames, img, annot_name, annot_data)
            self.redraw()

    def newImage(self, image_path, image, annot_path, annot):
        self.image_path = image_path
	self.image_extension = os.path.splitext(self.image_path)[1]
        self.image = image.copy()
        self.annot_path = annot_path
        self.annot = annot
        self.annot_coords = [[0, 0], [0, 0], [0, 0], [0, 0]]  # x;y
        self.label_image.updatePixmap(QtGui.QPixmap.fromImage(mat_to_qimage(self.image)))

    def point_selected(self, x1, y1, x2 ,y2, button):
        if button != 1 and button != 2:
            return
        if button == 1:
            # new annotation point
            w = float(x2-x1)
            h = float(y2-y1)
            rect = ((float(x1)+(w/2),float(y1)+(h/2)),(w,h),0.0)  
            self.annot.append(Annot(rect, self.classIndx))   #Add ID of seleted Class
        if button == 2:                     # remove existing annotation
            id = 0
            del_id = -1
            for an in self.annot:
                tmp = np.zeros(self.image.shape[:2], dtype=np.uint8)
                bp = cv2.boxPoints(an.rect)
                bp = np.int0(bp)
                cv2.drawContours(tmp, [bp], 0, (255), -1)
                if tmp[y1, x1] > 0:
                    del_id = id
                    break
                id += 1
            if del_id >= 0:
                del self.annot[del_id]
        self.redraw()

    def redraw(self):
        vis = self.image.copy()
        id = 1
        for an in self.annot:
            bp = cv2.boxPoints(an.rect)
            bp = np.int0(bp)
            cv2.drawContours(vis, [bp], 0, (0, 0, 255),3)
            cv2.putText(vis, '{}'.format(self.classList[int(an.classIndex)]), (bp[0, 0]+5, bp[0, 1]-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
            id += 1

        self.label_image.setPixmap(QtGui.QPixmap.fromImage(mat_to_qimage(vis)))
        self.label_image.setGeometry(QtCore.QRect(0, 0, vis.shape[1], vis.shape[0]))
        self.label_image.updatePixmap(QtGui.QPixmap.fromImage(mat_to_qimage(vis)))

    def fetchNextImage(self):
        if self.image_path is not None:
            path, _ = os.path.split(self.image_path)
            filesImage = glob.glob(path+'/*.jpg')+glob.glob(path+'/*.png')+glob.glob(path+'/*.jpeg')
            indexOfImage = filesImage.index(self.image_path)
            if len(filesImage) > indexOfImage:
                img = cv2.imread(filesImage[indexOfImage+1])
                annot_name = os.path.join(os.path.dirname(filesImage[indexOfImage+1]), '{}.txt'.format(os.path.splitext(filesImage[indexOfImage+1])[0]))
                annot_data = []
                if os.path.isfile(annot_name):
                    print('Loading existing annotation file')
                    annot_data = parse_annotation_file(annot_name,img.shape[0],img.shape[1])
                self.newImage(filesImage[indexOfImage+1], img, annot_name, annot_data)
                self.redraw()

    def fetchPreviousImage(self):
        if self.image_path is not None:
            path, _ = os.path.split(self.image_path)
            filesImage = glob.glob(path+'/*.jpg')+glob.glob(path+'/*.png')+glob.glob(path+'/*.jpeg')
            indexOfImage = filesImage.index(self.image_path)
            if indexOfImage > 0:
                img = cv2.imread(filesImage[indexOfImage-1])
                annot_name = os.path.join(os.path.dirname(filesImage[indexOfImage-1]), '{}.txt'.format(os.path.splitext(filesImage[indexOfImage-1])[0]))
                annot_data = []
                if os.path.isfile(annot_name):
                    print('Loading existing annotation file')
                    annot_data = parse_annotation_file(annot_name,img.shape[0],img.shape[1])
                self.newImage(filesImage[indexOfImage-1], img, annot_name, annot_data)
                self.redraw()

    def saveAnnotation(self):
        print('Writing annotation data to "{}"'.format(self.annot_path))
        write_annotation_file(self.annot, self.annot_path,self.image.shape[0],self.image.shape[1])

    def selectionchange(self,i):
        self.classIndx = i

    def rotate3Image(self):
        rotated1 = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        write_annotation_file_90(self.annot, (os.path.splitext(self.annot_path)[0]+'_r90.txt'),self.image.shape[0],self.image.shape[1])
        cv2.imwrite((os.path.splitext(self.annot_path)[0]+'_r90'+self.image_extension),rotated1)
        rotated2 = cv2.rotate(self.image, cv2.ROTATE_180)
        write_annotation_file_180(self.annot, (os.path.splitext(self.annot_path)[0]+'_r180.txt'),self.image.shape[0],self.image.shape[1])
        cv2.imwrite((os.path.splitext(self.annot_path)[0]+'_r180'+self.image_extension),rotated2)
        rotated3 = cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        write_annotation_file_270(self.annot, (os.path.splitext(self.annot_path)[0]+'_r270.txt'),self.image.shape[0],self.image.shape[1])
        cv2.imwrite((os.path.splitext(self.annot_path)[0]+'_r270'+self.image_extension),rotated3)

    def addnoiseImage(self):
        img = self.image.copy()
        noiseImage = cv2.randn(img,(0,0,0),(5,5,5))
        write_annotation_file(self.annot, (os.path.splitext(self.annot_path)[0]+'_n1.txt'),self.image.shape[0],self.image.shape[1])
        cv2.imwrite((os.path.splitext(self.annot_path)[0]+'_n1'+self.image_extension),(self.image+noiseImage))
        img2 = self.image.copy()
        noiseImage2 = cv2.randn(img2,(0,0,0),(10,10,10))
        write_annotation_file(self.annot, (os.path.splitext(self.annot_path)[0]+'_n2.txt'),self.image.shape[0],self.image.shape[1])
        cv2.imwrite((os.path.splitext(self.annot_path)[0]+'_n2'+self.image_extension),(self.image+noiseImage2))

    def addBrightImage(self):
        frameBright1 = increase_brightness(self.image, value=10)
        write_annotation_file(self.annot, (os.path.splitext(self.annot_path)[0]+'_b1.txt'),self.image.shape[0],self.image.shape[1])
        cv2.imwrite((os.path.splitext(self.annot_path)[0]+'_b1'+self.image_extension),(frameBright1))
        frameBright2 = increase_brightness(self.image, value=20)
        write_annotation_file(self.annot, (os.path.splitext(self.annot_path)[0]+'_b2.txt'),self.image.shape[0],self.image.shape[1])
        cv2.imwrite((os.path.splitext(self.annot_path)[0]+'_b2'+self.image_extension),(frameBright2))

    def flippingImage(self):
        horizontal_img = cv2.flip( self.image, 1)
        write_annotation_file_flip(self.annot, (os.path.splitext(self.annot_path)[0]+'_f.txt'),self.image.shape[0],self.image.shape[1])
        cv2.imwrite((os.path.splitext(self.annot_path)[0]+'_f'+self.image_extension),(horizontal_img))

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Save?', 'Save changes to file?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            print('Writing annotation data to "{}"'.format(self.annot_path))
            write_annotation_file(self.annot, self.annot_path, self.image.shape[0],self.image.shape[1])
        event.accept()


app = QtGui.QApplication(sys.argv)
win = Window()
win.show()

sys.exit(app.exec_())
