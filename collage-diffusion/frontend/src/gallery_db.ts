const gallery_db = [
    {
        "imgSrc": ""
    }
]

export function addImageToGallery(imgSrc: string) {
    gallery_db.push({
        imgSrc: imgSrc
    });
}

export default gallery_db;