import subprocess
import json
import os
import boto3
import urllib.request
import cv2
import random
import argparse

def detect_custom_labels(image_path, bucket_name, folder_path, model_arn):
    # AWS Rekognition command
    aws_command = f"""aws rekognition detect-custom-labels \
        --project-version-arn "{model_arn}" \
        --image '{{"S3Object": {{"Bucket": "{bucket_name}","Name": "{image_path}"}}}}' \
        --region us-east-1"""
    
    # Execute AWS CLI command
    result = subprocess.run(aws_command, capture_output=True, text=True, shell=True)
    
    # Check if the command was successful
    if result.returncode == 0:
        # Write the response to a JSON file in the specified folder with the same name as the image
        json_response = json.loads(result.stdout)
        output_filename = os.path.join(folder_path, os.path.splitext(os.path.basename(image_path))[0] + ".json")
        with open(output_filename, "w") as outfile:
            json.dump(json_response, outfile, indent=4)
        print(f"Detection result saved to {output_filename}")
        return output_filename
    else:
        print("Error executing AWS CLI command:")
        print(result.stderr)
        return None

def download_image_from_s3(bucket_name, image_key, local_path):
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, image_key, local_path)
        print(f"Image downloaded from S3: {local_path}")
        return True
    except Exception as e:
        print(f"Error downloading image from S3: {e}")
        return False

def draw_bounding_boxes(image_path, json_response, output_image_path):
    # Read the image
    image = cv2.imread(image_path)
    
    # Get image dimensions
    height, width, _ = image.shape
    
    # Define colors for bounding boxes
    label_colors = {}
    
    # Loop through the custom labels and assign a color to each label
    for label in json_response["CustomLabels"]:
        if label["Name"] not in label_colors:
            # Generate a random color for the label
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            label_colors[label["Name"]] = color
    
    # Loop through the custom labels and draw bounding boxes
    for label in json_response["CustomLabels"]:
        box = label["Geometry"]["BoundingBox"]
        x = int(box["Left"] * width)
        y = int(box["Top"] * height)
        w = int(box["Width"] * width)
        h = int(box["Height"] * height)
        
        # Get color for the label
        color = label_colors[label["Name"]]
        
        # Draw bounding box
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, label["Name"], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Save image with bounding boxes
    cv2.imwrite(output_image_path, image)
    print(f"Image with bounding boxes saved to {output_image_path}")

def main():
    parser = argparse.ArgumentParser(description="Detect custom labels in an image using AWS Rekognition and draw bounding boxes.")
    parser.add_argument("image_path", type=str, help="Path to the image file")
    parser.add_argument("--bucket_name", type=str, default="ai-cane", help="Name of the S3 bucket containing the image")
    parser.add_argument("--folder_path", type=str, default="/home/fti-starawade/result", help="Path to the folder to save results")
    parser.add_argument("--model_arn", type=str, required=True, help="ARN of the custom model")
    args = parser.parse_args()

    # Detect custom labels and save the response to a JSON file
    json_file_path = detect_custom_labels(args.image_path, args.bucket_name, args.folder_path, args.model_arn)

    # If JSON file successfully created, proceed to download image and draw bounding boxes
    if json_file_path:
        # Download the image from S3
        download_success = download_image_from_s3(args.bucket_name, args.image_path, os.path.basename(args.image_path))
        
        # If image downloaded successfully, draw bounding boxes
        if download_success:
            # Load JSON response
            with open(json_file_path, "r") as json_file:
                json_response = json.load(json_file)
            
            # Path to save the image with bounding boxes
            output_image_path = os.path.join(args.folder_path, os.path.splitext(os.path.basename(args.image_path))[0] + "_with_boxes.jpg")
            
            # Draw bounding boxes on the image and save it
            draw_bounding_boxes(os.path.basename(args.image_path), json_response, output_image_path)
            
            # Show the image with bounding boxes
            img = cv2.imread(output_image_path)
            cv2.imshow('Image with Bounding Boxes', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
