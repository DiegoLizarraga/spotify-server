import os

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException


class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True
        )

    async def upload_image(self, file: UploadFile, folder: str = "postify") -> dict:
        try:
            contents = await file.read()
            upload_result = cloudinary.uploader.upload(
                contents,
                folder=folder,
                resource_type="image",
                transformation=[
                    {"width": 1000, "height": 1000}
                ]
            )
            return {
                "url": upload_result["secure_url"],
                 "public_id": upload_result["public_id"]}
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error uploading image: {str(e)}"
                )
        

    def delete_image(self, public_id: str) -> dict:
        result = cloudinary.uploader.destroy(public_id)
        return result


cloudinary_service = CloudinaryService()