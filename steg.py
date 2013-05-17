import Image
import sys
import random

SIZE_T = 32

def RetrieveData(image, seed):
    w,h = image.size
    img = image.load()
    random.seed(seed)

    template = []
    for j in range(0, h):
        for i in range(0, w):
            template.append((i, j))
    random.shuffle(template)

    bits = 0
    data = []
    size = 10000
    end = False
    header_ok = False
    while not end:
        if bits >= SIZE_T and header_ok == False:
            size = parseHeader(data[:SIZE_T])
            data = data[SIZE_T:]
            header_ok = True

        rd = random.randint(0, len(template)-1) 
        pixel = template[rd]
        template.pop(rd)
        pix = random.randint(0, 2) 

        for jj in range(0, 3):
            data.append(img[pixel[0], pixel[1]][pix] & 0x1)
            pix = (pix + 1)%3
            bits += 1
            if bits >= size + SIZE_T:
                end = True
                break

    return ToByteArray(data)

def ToByteArray(data):
    byte_array = []

    j = 0
    temp = 0
    for i in data:
        temp = temp | (i << j)
        j += 1
        if j == 8:
            byte_array.append(temp)
            temp = 0
            j = 0

    return byte_array
def parseHeader(bit_array):
    sz = 0
    for i in range(0, len(bit_array)):
        sz = sz | (bit_array[i] << i)

    return sz

def HideData(image, data, seed):
    lin_image = LinearizeBits(data)
    header = [len(lin_image)]
    lin_header = LinearizeBits(header)
    w,h = image.size
    img = image.load()
    random.seed(seed)


    if len(lin_image)/8.0 >= (3.0*w*h/8) - 12:
        print "The file you're trying cannot be hidden in this image. Capacity: " + str((w*h*3.0)/8 - 12) + ".File: " + str(len(lin_image))
        return

    template = []
    for j in range(0, h):
        for i in range(0, w):
            template.append((i, j))

    random.shuffle(template)

    lin_data = lin_header + lin_image
    while len(lin_data) > 0 and len(template) > 0:
        rd = random.randint(0, len(template)-1)
        pair = template[rd]
        template.pop(rd)

        pix = random.randint(0, 2) 
       
        for jj in range(0, 3):
            pixel = list(img[pair[0], pair[1]])
            pixel[pix] = ((pixel[pix] >> 1) << 1) | lin_data[0]
            img[pair[0],pair[1]] = tuple(pixel)
            lin_data.pop(0)
            if len(lin_data) == 0:
                break
            pix = (pix + 1)%3

    return image

def LinearizeBits(data):
    bit_buffer = []
    
    if type(data[0]) != int:
        for i in data:
            for j in range(0, 8):
                bit_buffer.append(((0x1 << j)&ord(i)) >> j)
    else:
        for i in data:
            for j in range(0, SIZE_T):
                bit_buffer.append(((0x1 << j)&i) >> j)
  
    return bit_buffer

def ToArray(f):
    lin = []

    while True:
        byte = f.read(1)
        if byte != "":
            lin.append(byte)
        else:
            break

    return lin

# arg[1] = Mode
if sys.argv[1] == "hide":
    # arg[2] = Path to image
    # arg[3] = Data to be hidden
    # arg[4] = key to use as seed
    # arg[5] = output file(use PNG)
    HideData(Image.open(sys.argv[2]), ToArray(open(sys.argv[3], "rb")), int(sys.argv[4])).save(sys.argv[5])
else:
    if sys.argv[1] == "get":
        f = open(sys.argv[4], "wb")
        for c in RetrieveData(Image.open(sys.argv[2]), int(sys.argv[3])):
            f.write(chr(c))

        f.close()
