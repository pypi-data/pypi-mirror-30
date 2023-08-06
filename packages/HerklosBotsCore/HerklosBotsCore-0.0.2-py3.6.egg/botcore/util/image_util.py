def convert_image_to_bytes(image):
    with open(image, "rb") as imageFile:
        file = imageFile.read()
        bytes_result = bytearray(file)
    return bytes_result
