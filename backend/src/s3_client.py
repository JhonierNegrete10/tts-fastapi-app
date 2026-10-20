# import boto3
# from botocore.exceptions import ClientError

# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),

# )



# @app.get("/audio/{record_id}")
# async def get_audio(record_id: str, session: Session = Depends(get_session)):
#     record = speech_records.get_by_id(db=session, record_id=record_id)
#     if not record:
#         raise HTTPException(status_code=404, detail="Record not found")
#     try:
#         # Get S3 URL from your database
#         s3_url = record.audio_file  # Your database query here

#         # Parse bucket and key from S3 URL
#         bucket_name = s3_url.split("/")[2].split(".")[0]
#         key = "/".join(s3_url.split("/")[3:])

#         # Get object from S3
#         file_obj = s3_client.get_object(Bucket=bucket_name, Key=key)

#         # Return streaming response
#         return StreamingResponse(
#             file_obj["Body"].iter_chunks(),
#             media_type="audio/wav",  # Adjust content type as needed
#             headers={"Content-Disposition": f'attachment; filename="{key}"'},
#         )
#     except ClientError as e:
#         raise HTTPException(status_code=404, detail=f"Audio file not found {e}")
