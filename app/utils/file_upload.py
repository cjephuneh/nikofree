import os
import uuid
import requests
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
import io


def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'pdf'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def optimize_image(image_path, max_width=1920, max_height=1920, quality=85):
    """
    Optimize image by resizing and compressing
    
    Args:
        image_path: Path to the image file
        max_width: Maximum width in pixels (default: 1920)
        max_height: Maximum height in pixels (default: 1920)
        quality: JPEG quality 1-100 (default: 85)
    
    Returns:
        str: Path to optimized image (may be different if PNG converted to JPEG)
    """
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Get original dimensions
            original_width, original_height = img.size
            
            # Calculate new dimensions maintaining aspect ratio
            if original_width > max_width or original_height > max_height:
                ratio = min(max_width / original_width, max_height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            ext = os.path.splitext(image_path)[1].lower()
            if ext in ['.jpg', '.jpeg']:
                img.save(image_path, 'JPEG', quality=quality, optimize=True)
                return image_path
            elif ext == '.png':
                # PNG optimization - convert to JPEG if it's a photo (not transparent)
                if img.mode == 'RGB':
                    # Convert PNG to JPEG for better compression
                    jpeg_path = os.path.splitext(image_path)[0] + '.jpg'
                    img.save(jpeg_path, 'JPEG', quality=quality, optimize=True)
                    # Replace PNG with JPEG
                    if os.path.exists(jpeg_path):
                        os.remove(image_path)
                        return jpeg_path
                else:
                    # Keep PNG if it has transparency
                    img.save(image_path, 'PNG', optimize=True)
                    return image_path
            else:
                # For other formats, just save as-is
                img.save(image_path, optimize=True)
                return image_path
    except Exception as e:
        current_app.logger.warning(f"Image optimization failed: {str(e)}")
        # Return original path if optimization fails
        return image_path


def upload_file(file, folder='general', optimize=True):
    """
    Upload file and return path
    
    Args:
        file: FileStorage object from request
        folder: Subfolder name (e.g., 'events', 'partners', 'logos')
        optimize: Whether to optimize images (default: True)
        
    Returns:
        str: Relative path to uploaded file or None if failed
    """
    if not file or file.filename == '':
        return None
    
    # Check if filename is actually a base64 data URI (shouldn't happen, but prevent it)
    if file.filename and file.filename.startswith('data:image'):
        raise ValueError('Base64 data URIs are not allowed. Please upload an actual image file.')
    
    if not allowed_file(file.filename):
        raise ValueError('File type not allowed')
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    
    # Create upload directory
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    target_folder = os.path.join(upload_folder, folder)
    os.makedirs(target_folder, exist_ok=True)
    
    # Save file
    filepath = os.path.join(target_folder, unique_filename)
    file.save(filepath)
    
    # Optimize image if it's an image file
    if optimize:
        ext_lower = ext.lower()
        if ext_lower in ['.jpg', '.jpeg', '.png']:
            # Set max dimensions based on folder type
            if folder == 'events':
                max_width, max_height = 1920, 1920  # Event posters can be larger
            elif folder == 'logos':
                max_width, max_height = 800, 800  # Logos should be smaller
            elif folder == 'profiles':
                max_width, max_height = 800, 800  # Profile pictures
            else:
                max_width, max_height = 1920, 1920  # Default
            
            optimized_path = optimize_image(filepath, max_width=max_width, max_height=max_height, quality=85)
            if optimized_path and optimized_path != filepath:
                # If PNG was converted to JPEG, update the filename and path
                unique_filename = os.path.basename(optimized_path)
                filepath = optimized_path
    
    # Return relative path
    return f"/uploads/{folder}/{unique_filename}"


def delete_file(filepath):
    """Delete file from filesystem"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
    return False


def download_image_from_url(image_url, folder='profiles'):
    """
    Download image from URL and save to uploads folder
    
    Args:
        image_url: URL of the image to download
        folder: Subfolder name (e.g., 'profiles', 'events')
        
    Returns:
        str: Relative path to downloaded file or None if failed
    """
    if not image_url:
        return None
    
    try:
        # Download image
        response = requests.get(image_url, timeout=10, stream=True)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print(f"Warning: URL does not point to an image. Content-Type: {content_type}")
            return None
        
        # Determine file extension from content type or URL
        ext = '.jpg'  # default
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        elif 'gif' in content_type:
            ext = '.gif'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            # Try to get extension from URL
            url_lower = image_url.lower()
            if url_lower.endswith('.png'):
                ext = '.png'
            elif url_lower.endswith('.jpg') or url_lower.endswith('.jpeg'):
                ext = '.jpg'
            elif url_lower.endswith('.gif'):
                ext = '.gif'
            elif url_lower.endswith('.webp'):
                ext = '.webp'
        
        # Generate unique filename
        unique_filename = f"profile_{uuid.uuid4().hex[:12]}{ext}"
        
        # Create upload directory
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        target_folder = os.path.join(upload_folder, folder)
        os.makedirs(target_folder, exist_ok=True)
        
        # Save file
        filepath = os.path.join(target_folder, unique_filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Return relative path
        return f"/uploads/{folder}/{unique_filename}"
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from URL: {str(e)}")
        return None
    except Exception as e:
        print(f"Error saving downloaded image: {str(e)}")
        return None


# For AWS S3 upload (optional)
def upload_to_s3(file, folder='general'):
    """
    Upload file to AWS S3
    
    Args:
        file: FileStorage object
        folder: S3 folder/prefix
        
    Returns:
        str: S3 URL or None if failed
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        if not file or file.filename == '':
            return None
        
        if not allowed_file(file.filename):
            raise ValueError('File type not allowed')
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{folder}/{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY'),
            region_name=current_app.config.get('AWS_REGION')
        )
        
        # Upload file
        bucket_name = current_app.config.get('AWS_S3_BUCKET')
        s3_client.upload_fileobj(
            file,
            bucket_name,
            unique_filename,
            ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type}
        )
        
        # Return S3 URL
        return f"https://{bucket_name}.s3.amazonaws.com/{unique_filename}"
        
    except ClientError as e:
        print(f"Error uploading to S3: {str(e)}")
        return None
    except ImportError:
        print("boto3 not installed. Using local file upload instead.")
        return upload_file(file, folder)

