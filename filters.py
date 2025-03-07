from PIL import Image, ImageFilter, ImageEnhance
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os

def apply_filter(image_path, filter_type):
    image = Image.open(image_path)
    
    if filter_type == 'blur':
        image = image.filter(ImageFilter.BLUR)
    elif filter_type == 'sharpen':
        image = image.filter(ImageFilter.SHARPEN)
    elif filter_type == 'grayscale':
        image = image.convert('L')
    elif filter_type == 'enhance':
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_path = 'output/processed_image.jpg'
    image.save(output_path)
    image.save(output_path)
    return output_path

def apply_video_filter(video_path, filter_type, text=None):
    video = VideoFileClip(video_path)
    
    if filter_type == 'add_text':
        txt_clip = TextClip(text, fontsize=50, color='white', bg_color='black')
        txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(video.duration)
    output_path = 'output/processed_video.mp4'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    output_path = 'output/processed_video.mp4'
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path