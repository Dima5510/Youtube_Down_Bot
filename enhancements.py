import cv2
import os

def enhance_quality(image_path, quality_level):
    img = cv2.imread(image_path)
    
    if img is None:
        raise ValueError("Image not found or unable to load.")
    
    if quality_level == 'low':
        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    elif quality_level == 'medium':
        img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    elif quality_level == 'high':
        img = cv2.resize(img, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
    
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, 'enhanced_image.jpg')
    cv2.imwrite(output_path, img)
    return output_path