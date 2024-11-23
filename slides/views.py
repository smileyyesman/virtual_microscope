from django.shortcuts import render
import openslide
from .models import SlideImage
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openslide.deepzoom import DeepZoomGenerator

@csrf_exempt
def view_slide(request, slide_id):
    slide_image = SlideImage.objects.get(id=slide_id)
    file_path = slide_image.image.path
    file_name = os.path.basename(file_path)

    # OpenSlide로 NDPI 파일 열기
    slide = openslide.OpenSlide(file_path)
    
    # DeepZoomGenerator 객체 생성
    dz = DeepZoomGenerator(slide, tile_size=254, overlap=1, limit_bounds=False)
    
    # DZI 파일 생성 및 저장
    dzi_name = os.path.splitext(file_name)[0] + '.dzi'
    dzi_path = os.path.join(settings.MEDIA_ROOT, 'dzi_files', dzi_name)
    dzi_url = settings.MEDIA_URL + 'dzi_files/' + dzi_name

    os.makedirs(os.path.dirname(dzi_path), exist_ok=True)
    
    with open(dzi_path, 'w') as f:
        f.write(dz.get_dzi("jpeg"))
    
    # 타일 이미지 생성
    tiles_dir = os.path.splitext(dzi_path)[0] + '_files'
    if not os.path.exists(tiles_dir):
        os.makedirs(tiles_dir)
    
    for level in range(dz.level_count):
        level_dir = os.path.join(tiles_dir, str(level))
        os.makedirs(level_dir, exist_ok=True)
        for col in range(dz.level_tiles[level][0]):
            for row in range(dz.level_tiles[level][1]):
                tile = dz.get_tile(level, (col, row))
                tile_path = os.path.join(level_dir, f"{col}_{row}.jpeg")
                tile.save(tile_path, quality=90)
    
    slide.close()
    
    return render(request, 'slides/view_slide.html', {'slide_url': dzi_url})
# Create your views here.
