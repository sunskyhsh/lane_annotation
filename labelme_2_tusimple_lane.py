#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
labelme标注结果转换为tusimple车道线数据集格式
'''
from __future__ import print_function
import json
import numpy as np
from logger import logger
import argparse
import base64
import os
import os.path as osp
import sys
import time

import PIL.Image
import math
import PIL.ImageDraw


def lblsave(filename, lbl):
    # if osp.splitext(filename)[1] != '.png':
    #     filename += '.png'
    # Assume label ranses [-1, 254] for int32,
    # and [0, 255] for uint8 as VOC.
    if lbl.min() >= -1 and lbl.max() < 255:
        lbl_pil = PIL.Image.fromarray(lbl.astype(np.uint8), mode='P')
        # colormap = label_colormap(255)
        # lbl_pil.putpalette((colormap * 255).astype(np.uint8).flatten())
        lbl_pil.save(filename)
    else:
        logger.warn(
            '[%s] Cannot save the pixel-wise class label as PNG, '
            'so please use the npy file.' % filename
        )

def shape_to_mask(img_shape, points, shape_type=None,
                  line_width=10, point_size=5):
    mask = np.zeros(img_shape[:2], dtype=np.uint8)
    mask = PIL.Image.fromarray(mask)
    draw = PIL.ImageDraw.Draw(mask)
    xy = [tuple(point) for point in points]
    if shape_type == 'circle':
        assert len(xy) == 2, 'Shape of shape_type=circle must have 2 points'
        (cx, cy), (px, py) = xy
        d = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
        draw.ellipse([cx - d, cy - d, cx + d, cy + d], outline=1, fill=1)
    elif shape_type == 'rectangle':
        assert len(xy) == 2, 'Shape of shape_type=rectangle must have 2 points'
        draw.rectangle(xy, outline=1, fill=1)
    elif shape_type == 'line':
        assert len(xy) == 2, 'Shape of shape_type=line must have 2 points'
        draw.line(xy=xy, fill=1, width=line_width)
    elif shape_type == 'linestrip':
        draw.line(xy=xy, fill=1, width=line_width)
    elif shape_type == 'point':
        assert len(xy) == 1, 'Shape of shape_type=point must have 1 points'
        cx, cy = xy[0]
        r = point_size
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=1, fill=1)
    else:
        assert len(xy) > 2, 'Polygon must have points more than 2'
        draw.polygon(xy=xy, outline=1, fill=1)
    mask = np.array(mask, dtype=bool)
    return mask


def shapes_to_label(img_shape, shapes, label_name_to_value, type='class'):
    assert type in ['class', 'instance']

    cls = np.zeros(img_shape[:2], dtype=np.int32)
    if type == 'instance':
        ins = np.zeros(img_shape[:2], dtype=np.int32)
        instance_names = ['_background_']
    for shape in shapes:
        points = shape['points']
        label = shape['label']
        shape_type = shape.get('shape_type', None)
        if type == 'class':
            cls_name = label
        elif type == 'instance':
            cls_name = label.split('-')[0]
            if label not in instance_names:
                instance_names.append(label)
            ins_id = instance_names.index(label)
        # cls_id = label_name_to_value[cls_name]
        cls_id = 255
        mask = shape_to_mask(img_shape[:2], points, shape_type)
        cls[mask] = cls_id
        if type == 'instance':
            ins[mask] = ins_id

    if type == 'instance':
        return cls, ins
    return cls

def single_json_2_image():
    logger.warning('This function is aimed to demonstrate how to convert the'
                   'JSON file to a single image dataset, and not to handle'
                   'multiple JSON files to generate a real-use dataset.')

    parser = argparse.ArgumentParser()
    parser.add_argument('json_file')
    parser.add_argument('-o', '--out', default=None)
    args = parser.parse_args()

    json_file = args.json_file

    if args.out is None:
        out_dir = osp.basename(json_file).replace('.', '_')
        out_dir = osp.join(osp.dirname(json_file), out_dir)
    else:
        out_dir = args.out
    if not osp.exists(out_dir):
        os.mkdir(out_dir)

    data = json.load(open(json_file))

    # read original image
    # if data['imageData']:
    #     imageData = data['imageData']
    # else:
    #     imagePath = os.path.join(os.path.dirname(json_file), data['imagePath'])
    #     with open(imagePath, 'rb') as f:
    #         imageData = f.read()
    #         imageData = base64.b64encode(imageData).decode('utf-8')
    # img = utils.img_b64_to_arr(imageData)

    img_width = data['imageWidth']
    img_height = data['imageHeight']

    label_name_to_value = {'_background_': 0}
    for shape in sorted(data['shapes'], key=lambda x: x['label']):
        label_name = shape['label']
        # if label_name in label_name_to_value:
        #     label_value = label_name_to_value[label_name]
        # else:
        if label_name not in label_name_to_value:
            label_value = len(label_name_to_value)
            label_name_to_value[label_name] = label_value
    lbl = shapes_to_label((img_width, img_height), data['shapes'], label_name_to_value)

    # label_names = [None] * (max(label_name_to_value.values()) + 1)
    # for name, value in label_name_to_value.items():
    #     label_names[value] = name
    # lbl_viz = utils.draw_label(lbl, img, label_names)

    # PIL.Image.fromarray(img).save(osp.join(out_dir, 'img.png'))
    lblsave(osp.join(out_dir, data['imagePath'].split('.')[0] + '_label.png'), lbl)
    # PIL.Image.fromarray(lbl_viz).save(osp.join(out_dir, 'label_viz.png'))

    # with open(osp.join(out_dir, 'label_names.txt'), 'w') as f:
    #     for lbl_name in label_names:
    #         f.write(lbl_name + '\n')

    # logger.warning('info.yaml is being replaced by label_names.txt')
    # info = dict(label_names=label_names)
    # with open(osp.join(out_dir, 'info.yaml'), 'w') as f:
    #     yaml.safe_dump(info, f, default_flow_style=False)

    # logger.info('Saved to: {}'.format(out_dir))

def json_2_image():
    '''
    This file is to transform the json files generated by labelme 
    for the lane images to binary images and instance images according 
    to the tusimple lane dataset format.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('json_files_path', type=str, help='The path of the folder containing the json files generated by labelme')
    parser.add_argument('-o', '--out', default='.', type=str, help='The output direcotory of the dataset. Default is current folder.')
    args = parser.parse_args()

    json_files_path = args.json_files_path
    files = os.listdir(json_files_path)
    image_num = 0
    binary_out_dir = osp.join(args.out, 'gt_image_binary')
    instance_out_dir = osp.join(args.out, 'gt_image_instance')
    if not os.path.exists(binary_out_dir):
        os.makedirs(binary_out_dir)
    if not os.path.exists(instance_out_dir):
        os.makedirs(instance_out_dir)
    progress_bar_length = 50
    num_json_file = len(files)
    for json_file_name in files:
        if json_file_name.split('.')[-1] != 'json':
            continue
        data = json.load(open(osp.join(json_files_path, json_file_name)))
        image_name = data['imagePath'].split('.')[0]
        image_width = data['imageWidth']
        image_height = data['imageHeight']
        binary_image = np.zeros((image_height, image_width), np.uint8) # 0 and 255
        instance_image = binary_image.copy() # different gray value for different lane
        num_shape = len(data['shapes'])
        instance_gray_value_increment = np.floor(255 / num_shape)
        for idx in range(num_shape):
            shape = data['shapes'][idx]
            points = shape['points']
            label = shape['label']
            shape_type = shape.get('shape_type', None)
            mask = shape_to_mask((image_height, image_width), points, shape_type)
            binary_image[mask] = 255
            instance_image[mask] = (idx+1) * instance_gray_value_increment
        binary_image_filename = osp.join(binary_out_dir, image_name + ".png")
        instance_image_filename = osp.join(instance_out_dir, image_name + ".png")
        binary_image_pil = PIL.Image.fromarray(binary_image, mode='L')
        binary_image_pil.save(binary_image_filename)
        instance_image_pil = PIL.Image.fromarray(instance_image, mode='L')
        instance_image_pil.save(instance_image_filename)
        image_num += 1
        percent = image_num / num_json_file
        hashes = '#' * int(percent * progress_bar_length)
        spaces = ' ' * (progress_bar_length - len(hashes))
        sys.stdout.write("\rProgress: [%s] %d%%"%(hashes + spaces, percent))
        sys.stdout.flush()
    sys.stdout.write("\rProgress: [%s] %d%%\n"%('#' * progress_bar_length, 100))
    sys.stdout.flush()
    return image_num

if __name__  ==  "__main__":
    time_start = time.time()
    image_num = json_2_image()
    time_end = time.time()
    logger.info('%d seconds elapsed for %d images' % (time_end-time_start, image_num))