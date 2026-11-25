import boto3
import urllib.parse
import os

s3 = boto3.client('s3')

# Replace with your exact destination bucket name
DEST_BUCKET = 'processed-files-2026'

def lambda_handler(event, context):
    # 1. Get the bucket name and file name from the S3 upload event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    file_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    file_size = event['Records'][0]['s3']['object']['size']
    
    # 2. Read the file extension to decide which folder it belongs in
    _, ext = os.path.splitext(file_key)
    ext = ext.lower()
    
    if ext in ['.jpg', '.jpeg', '.png', '.gif']:
        folder = 'images'
    elif ext in ['.pdf', '.docx', '.txt', '.csv']:
        folder = 'documents'
    else:
        folder = 'other'
        
    dest_key = f"{folder}/{file_key}"
    
    # 3. Copy the file to the processed bucket inside the sorted folder
    copy_source = {'Bucket': source_bucket, 'Key': file_key}
    s3.copy_object(CopySource=copy_source, Bucket=DEST_BUCKET, Key=dest_key)
    
    # 4. Log the details to CloudWatch
    print(f"SUCCESS: Processed '{file_key}' ({file_size} bytes)")
    print(f"SORTED TO: s3://{DEST_BUCKET}/{dest_key}")
    
    return {
        'statusCode': 200,
        'body': f"File {file_key} sorted into {folder}/"
    }
