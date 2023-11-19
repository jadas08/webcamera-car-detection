import os
from django.conf import settings

def media_files(request):
    raw_files = os.listdir(os.path.join(settings.MEDIA_ROOT, 'raw'))
    processed_files = os.listdir(os.path.join(settings.MEDIA_ROOT, 'processed'))
    return {
        'raw_files': raw_files,
        'processed_files': processed_files
    }

from .models import ImageRecord
def media_files2(request):
    # Retrieve all ImageRecord objects from the database
    image_records = ImageRecord.objects.all().order_by('-time_created')  # Assuming you want the latest 15

    # Create lists to hold the processed file information
    processed_files_info = []
    raw_files_info = []

    # Iterate over the queryset and process each ImageRecord object
    for record in image_records:
        processed_files_info.append({
            'name': record.processed_name,
            'time': record.time_created.strftime('%Y-%m-%d %H:%M:%S'),
            'id' : record.id
            #'url': record.processed_image.url
        })

        # Similarly for raw files, if needed
        raw_files_info.append({
            'name': record.raw_name,
            'time': record.time_created.strftime('%Y-%m-%d %H:%M:%S'),
            'id' : record.id
            #'url': record.raw_image.url
        })


    return {
        'raw_files': raw_files_info,
        'processed_files': processed_files_info
    }