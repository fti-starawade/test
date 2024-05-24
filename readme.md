# Custom Label Detection with AWS Rekognition

This script detects custom labels in an image using AWS Rekognition and draws bounding boxes around the detected objects.

## Requirements

- Python 3.x
- AWS CLI configured with necessary permissions
- OpenCV (cv2) library
- boto3 library

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your_username/your_repository.git
cd your_repository
```

2. Install the required Python libraries:

```bash
pip install -r requirements.txt
```

## Usage

1. Configure your AWS CLI with the necessary permissions.

2. Run the script:

```bash
python detect_custom_labels.py image_path --model_arn "your_model_arn"
```

Replace `image_path` with the path to the image file you want to analyze. The `--model_arn` parameter is required and should be the ARN of your custom model in AWS Rekognition.

Optional parameters:

- `--bucket_name`: Name of the S3 bucket containing the image (default: ai-cane).
- `--folder_path`: Path to the folder to save results (default: /home/fti-starawade/result).

3. View the results:

The script will save the detection results as a JSON file and an image with bounding boxes in the specified folder path. Additionally, it will display the image with bounding boxes using OpenCV.
