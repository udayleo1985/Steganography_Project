from PIL import Image
import numpy as np

def text_to_binary(text):
    """
    Convert text string to a binary string.
    Each character converted to 8-bit binary.
    """
    binary = ''.join(format(ord(char), '08b') for char in text)
    return binary

def embed_text_in_image(image_path, secret_text, output_path):
    """
    Embed secret_text into the image located at image_path.
    Save the modified image at output_path.
    """
    # Load and prepare image
    image = Image.open(image_path)
    image = image.convert('RGB')  # Ensure RGB format
    data = np.array(image)

    # Convert secret text to binary and append delimiter
    binary_text = text_to_binary(secret_text) + '1111111111111110'  # Delimiter to mark end of message

    # Flatten image array to 1D for easy embedding
    data_flat = data.flatten()

    # Check if message fits into image
    if len(binary_text) > len(data_flat):
        raise ValueError("Error: Secret message too large to fit in image.")

    # Embed each bit of binary_text into LSB of pixel data
    for i in range(len(binary_text)):
        current_pixel_value = int(data_flat[i])  # Ensure integer type
        new_pixel_value = (current_pixel_value & ~1) | int(binary_text[i])

        if new_pixel_value < 0 or new_pixel_value > 255:
            raise OverflowError(f"Pixel value {new_pixel_value} out of bounds for uint8.")

        data_flat[i] = new_pixel_value

    # Reshape modified flat array back to original image shape
    stego_data = np.reshape(data_flat, data.shape)

    # Create and save stego image
    stego_image = Image.fromarray(stego_data.astype('uint8'), 'RGB')
    stego_image.save(output_path)
    print(f"[*] Secret message embedded and image saved at '{output_path}'")

def binary_to_text(binary):
    """
    Convert binary string to text.
    Stops decoding at delimiter '11111111' (part of delimiter).
    """
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    message = ''
    for char in chars:
        if char == '11111111':  # delimiter part, stop reading
            break
        message += chr(int(char, 2))
    return message

def extract_text_from_image(stego_image_path):
    """
    Extract hidden text from stego image at stego_image_path.
    """
    image = Image.open(stego_image_path)
    image = image.convert('RGB')
    data = np.array(image)
    data_flat = data.flatten()

    binary = ''
    for byte in data_flat:
        binary += str(byte & 1)
        if binary[-16:] == '1111111111111110':  # delimiter indicates end
            break

    # Remove delimiter bits
    binary = binary[:-16]
    secret_text = binary_to_text(binary)
    return secret_text

if __name__ == "__main__":
    cover_image_path = 'cover_image.png'   # Make sure this image exists in your folder
    stego_image_path = 'stego_image.png'   # Output image file
    secret_message = "This is my secret message!"  # Put your secret message here

    print("[*] Starting embedding process...")
    embed_text_in_image(cover_image_path, secret_message, stego_image_path)

    print("[*] Starting extraction process...")
    extracted_message = extract_text_from_image(stego_image_path)
    print(f"[*] Extracted message: '{extracted_message}'")
