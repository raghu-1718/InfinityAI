# DVC initialization script
# Run this script to initialize DVC in your project
import os
os.system('dvc init')
os.system('dvc remote add -d storage s3://your-bucket/dvc-storage')
# Example: dvc add data/dataset.csv
# Example: dvc push
