from motor.motor_asyncio import AsyncIOMotorGridFSBucket


async def upload_image_to_gridfs(db, filename: str, content_type: str, file_bytes: bytes):
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="waste_images")
    file_id = await bucket.upload_from_stream(
        filename,
        file_bytes,
        metadata={"content_type": content_type},
    )
    return file_id
