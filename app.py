from flask import Flask, render_template, request, jsonify
import os
import hashlib
import cv2
import numpy as np
import tempfile

app = Flask(__name__)

# Function to compute the MD5 hash of an image
def compute_md5(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
        return hashlib.md5(data).hexdigest()

# Function to calculate the difference between two images
def find_difference(original_img, modified_img):
    original = cv2.imread(original_img, cv2.IMREAD_GRAYSCALE)
    modified = cv2.imread(modified_img, cv2.IMREAD_GRAYSCALE)
    
    # Compute absolute difference
    difference = cv2.absdiff(original, modified)
    _, threshold_diff = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)
    
    return threshold_diff

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    show_image = False
    output_image = ""
    year = 2025  # You can make this dynamic if desired
    
    if request.method == 'POST':
        original_file = request.files['original']
        modified_file = request.files['modified']

        # Save the uploaded files to temporary locations
        with tempfile.NamedTemporaryFile(delete=False) as orig_temp, tempfile.NamedTemporaryFile(delete=False) as mod_temp:
            original_path = orig_temp.name
            modified_path = mod_temp.name
            original_file.save(original_path)
            modified_file.save(modified_path)
            
            # Compare MD5 hashes
            original_md5 = compute_md5(original_path)
            modified_md5 = compute_md5(modified_path)
            
            if original_md5 != modified_md5:
                # Find difference in images
                diff_img = find_difference(original_path, modified_path)
                diff_img_path = "static/difference.png"
                cv2.imwrite(diff_img_path, diff_img)
                result = "The images are modified (forged)."
                show_image = True
                output_image = diff_img_path
            else:
                result = "The images are identical."
    
    return render_template('index.html', result=result, show_image=show_image, output_image=output_image, year=year)

if __name__ == '__main__':
    app.run(debug=True)
