# 车道线数据标注说明

## 标注工具
### labelme：基于python的图像标注工具
#### 安装
参考[labelme](https://github.com/wkentaro/labelme)

在ubuntu下安装
```
# Ubuntu 14.04 / Ubuntu 16.04
# Python2
# sudo apt-get install python-qt4  # PyQt4
sudo apt-get install python-pyqt5  # PyQt5
sudo pip install labelme
# Python3
sudo apt-get install python3-pyqt5  # PyQt5
sudo pip3 install labelme
```

或者在Anaconda中安装：
```
# python2
conda create --name=labelme python=2.7
source activate labelme
# conda install -c conda-forge pyside2
conda install pyqt
pip install labelme
# if you'd like to use the latest version. run below:
# pip install git+https://github.com/wkentaro/labelme.git

# python3
conda create --name=labelme python=3.6
source activate labelme
# conda install -c conda-forge pyside2
# conda install pyqt
pip install pyqt5  # pyqt5 can be installed via pip on python3
pip install labelme
```

Windows下的安装方法是在Anaconda方法的基础上，再执行以下命令。
```
# Pillow 5 causes dll load error on Windows.
# https://github.com/wkentaro/labelme/pull/174
conda install pillow=4.0.0
```

#### 标注方法
命令行输入：
```
labelme --nodata --autosave
```
--nodata参数的作用是在标注结果中不保存原始图像数据，只保存标注信息。
--autosave参数的作用是在保存第一张图片标注结果后，之后的图片标注结果自动保存到同一目录。

标注界面打开后，可以点击“Open”打开单幅图像进行标注，也可以点击“Open Dir”打开图像文件夹。
标注模式有多种，可以标注出多边形、矩形、圆形、线段等。标注车道线一般使用多边形模式或者线模式。

####　线段模式
在打开的图片上右键，点击“Create Line”，然后在图片上点击车道线的两个端点，再给标签命名。
![标注线段][labelme-line.png]

#### 多边形模式
点击“Create Polygons”，然后在图片上画出包围车道线的多边形。
![标注多边形][labelme-polygon.png]

#### 标注结果
标注结果为json文件，其中关键参数为"imageWidth"、"imageHeight"、"imagePath"和"shapes"。
"shapes"是标注的线段、多边形等形状的位置。

## 格式转换
labelme_2_tusimple_lane.py为将标注结果转换为图森车道线数据集格式的脚本。

依赖库：logger、numpy

### 图森车道线数据集格式
格式为：
- data
  - image
  - gt_image_binary
  - gt_image_instance
  - train.txt
  - val.txt

image目录下为原始图像。
gt_image_binary目录下为二值化图像。
gt_image_instance目录下为灰度图像（不同车道线对应不同灰度值）。
train.txt为训练集路径。
val.txt为验证集路径。

### 转换方法
脚本labelme_2_tusimple_lane.py可以通过labelme标注得到的json文件生成gt_image_binary和gt_image_instance目录下的图像。
使用方法为在命令行输入：
```
python labelme_2_tusimple_lane.py [标注结果所在路径] [-o 输出路径（默认为当前路径）]
```
脚本会在输出路径下创建gt_image_binary和gt_image_instance目录，并在其中生成二指图像和灰度图像。
对于线段模式标注的车道线，得到的二值图像为：
![线段模式标注得到的二值图像][line.png]

对于多边形模式标注的车道线，得到的二值图像为：
![多边形模式标注得到的二值图像][polygon.png]