# -*- coding: utf-8 -*-

import os
import numpy as np
from xml.etree.ElementTree import parse


class PascalVocXmlParser(object):
    """Parse annotation for 1-annotation file """
    
    def __init__(self):
        pass

    def get_fname(self, annotation_file):
        """
        # Args
            annotation_file : str
                annotation file including directory path
        
        # Returns
            filename : str
        """
        root = self._root_tag(annotation_file)
        return root.find("filename").text

    def get_width(self, annotation_file):
        """
        # Args
            annotation_file : str
                annotation file including directory path
        
        # Returns
            width : int
        """
        tree = self._tree(annotation_file)
        for elem in tree.iter():
            if 'width' in elem.tag:
                return int(elem.text)

    def get_height(self, annotation_file):
        """
        # Args
            annotation_file : str
                annotation file including directory path
        
        # Returns
            height : int
        """
        tree = self._tree(annotation_file)
        for elem in tree.iter():
            if 'height' in elem.tag:
                return int(elem.text)

    def get_labels(self, annotation_file):
        """
        # Args
            annotation_file : str
                annotation file including directory path
        
        # Returns
            labels : list of strs
        """

        root = self._root_tag(annotation_file)
        labels = []
        obj_tags = root.findall("object")
        for t in obj_tags:
            labels.append(t.find("name").text)
        return labels
    
    def get_boxes(self, annotation_file):
        """
        # Args
            annotation_file : str
                annotation file including directory path
        
        # Returns
            bbs : 2d-array, shape of (N, 4)
                (x1, y1, x2, y2)-ordered
        """
        root = self._root_tag(annotation_file)
        bbs = []
        obj_tags = root.findall("object")
        for t in obj_tags:
            box_tag = t.find("bndbox")
            x1 = box_tag.find("xmin").text
            y1 = box_tag.find("ymin").text
            x2 = box_tag.find("xmax").text
            y2 = box_tag.find("ymax").text
            box = np.array([int(x1), int(y1), int(x2), int(y2)])
            bbs.append(box)
        bbs = np.array(bbs)
        return bbs

    def _root_tag(self, fname):
        tree = parse(fname)
        root = tree.getroot()
        return root

    def _tree(self, fname):
        tree = parse(fname)
        return tree
    


def parse_annotation(ann_dir, img_dir, labels=[]):
    """
    # Args
        ann_dir : str
        img_dir : str
    
    # Returns
        all_imgs : list of dict
        seen_labels : dict
            {'raccoon': 1, ...}
    """
    all_imgs = []
    seen_labels = {}
    
    parser = PascalVocXmlParser()
    
    for ann in sorted(os.listdir(ann_dir)):
        img = {'object':[]}
        
        annotation_file = os.path.join(ann_dir, ann)
        
        fname = parser.get_fname(annotation_file)
        img['filename'] = os.path.join(img_dir, fname)
        img['width'] = parser.get_width(annotation_file)
        img['height'] = parser.get_height(annotation_file)

        labels = parser.get_labels(annotation_file)
        boxes = parser.get_boxes(annotation_file)
        
        objects = []
        for label, box in zip(labels, boxes):
            x1, y1, x2, y2 = box
            objects.append({'name': label, 'xmin': x1, 'ymin': y1, 'xmax': x2, 'ymax': y2})
            
            if label in seen_labels:
                seen_labels[label] += 1
            else:
                seen_labels[label] = 1
        img['object'] = objects
        
        if len(img['object']) > 0:
            all_imgs += [img]
                        
    return all_imgs, seen_labels

