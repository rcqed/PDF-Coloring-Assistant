import os
from pdf2image import convert_from_path
from PIL import Image, ImageStat

def detect_color_image(image, thumb_size=40, MSE_cutoff=0.6, adjust_color_bias=True):
    pil_img = Image.open(image).convert("RGB")
    bands = pil_img.getbands()
    if bands == ('R', 'G', 'B') or bands == ('R', 'G', 'B', 'A'):
        thumb = pil_img.resize((thumb_size, thumb_size))
        SSE, bias = 0, [0, 0, 0]
        if adjust_color_bias:
            bias = ImageStat.Stat(thumb).mean[:3]
            bias = [b - sum(bias) / 3 for b in bias]
        for pixel in thumb.getdata():
            mu = sum(pixel) / 3
            SSE += sum((pixel[i] - mu - bias[i]) * (pixel[i] - mu - bias[i]) for i in [0, 1, 2])
        MSE = float(SSE) / (thumb_size * thumb_size)
        if MSE <= MSE_cutoff:
            return 'black_and_white'
        else:
            return 'color'
    elif len(bands) == 1:
        return 'black_and_white'
    else:
        return 'unknown'

def main():
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.lower().endswith('.pdf')]
    results = []

    for file in files:
        images = convert_from_path(file)

        color_pages = 0
        bw_pages = 0

        print(f"Processing file: {file}")

        for page_num, image in enumerate(images):
            image_path = f"page_{page_num}.png"
            image.save(image_path)

            color_type = detect_color_image(image_path)
            os.remove(image_path)

            if color_type == 'color':
                color_pages += 1
                print(f"Page {page_num + 1}: Color")
            elif color_type == 'black_and_white':
                bw_pages += 1
                print(f"Page {page_num + 1}: Black and White")

        result = f"File: {file}\nColor Pages: {color_pages}\nBlack and White Pages: {bw_pages}\n"
        results.append(result)

    with open('out.txt', 'w') as f:
        f.write('\n'.join(results))

if __name__ == '__main__':
    main()
