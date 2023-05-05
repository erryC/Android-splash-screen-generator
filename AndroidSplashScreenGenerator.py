import glob
import re
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

#settings
exportedImagesBitDepth = "RGB"


listPathImages = []
listImagesGUICrop = []
guiEls = []
listImagesLoaded = []
imagesSizes = []
logoImages = []
imagesCropped = []
imagesExportReady = []

ws = Tk()
ws.geometry("1200x720")
ws.title('Android splash screen generator')
cTableContainer = Canvas(ws)
fTable = Frame(cTableContainer)
sbHorizontalScrollBar = Scrollbar(ws)
sbVerticalScrollBar = Scrollbar(ws)

logo = Image.new(mode=exportedImagesBitDepth, size=(200, 200))
logoMini = ImageTk.PhotoImage(logo)

def updateScrollRegion():
	cTableContainer.update_idletasks()
	cTableContainer.config(scrollregion=fTable.bbox())
        
def createScrollableContainer():
	cTableContainer.config(xscrollcommand=sbHorizontalScrollBar.set,yscrollcommand=sbVerticalScrollBar.set, highlightthickness=0)
	sbHorizontalScrollBar.config(orient=HORIZONTAL, command=cTableContainer.xview)
	sbVerticalScrollBar.config(orient=VERTICAL, command=cTableContainer.yview)

	sbHorizontalScrollBar.pack(fill=X, side=BOTTOM, expand=FALSE)
	sbVerticalScrollBar.pack(fill=Y, side=RIGHT, expand=FALSE)
	cTableContainer.pack(fill=BOTH, side=LEFT, expand=TRUE)
	cTableContainer.create_window(0, 0, window=fTable, anchor=NW)


indexEl = 0
def updateGui():
    clearGui()
    global listPathImages, imagesSizes, listImagesGUICrop, guiEls
    for i in range(len(listPathImages)):
        fCropUndo = Frame(fTable)
        btnCrop = Button( fCropUndo, text ="Replace", command= lambda id=i: cropImage(id))
        btnUndo = Button( fCropUndo, text ="Undo", command= lambda id=i: undoCrop(id))
        guiEls.append(btnCrop)
        guiEls.append(btnUndo)
        btnCrop.pack(side="left")
        btnUndo.pack(side="right")

        img = openImg(listPathImages[i])
        imageGUI = ImgToLabel(img)
        listImagesGUICrop.append(imageGUI) #save reference to imagecrop GUI element

        fInfo = Frame(fTable)
        text = Label(fInfo, text=".."+shortenPath(listPathImages[i]), relief=RAISED )
        sizes = Label(fInfo, text=f'width: {imagesSizes[i][0]} height: {imagesSizes[i][1]}', relief=RAISED)
        guiEls.append(text)
        guiEls.append(sizes)
        text.pack(side="left")
        sizes.pack(side="right")
        
        packElement(fInfo)
        packElement(fCropUndo)
        packElement(imageGUI)

def packElement(el):
    global indexEl, guiEls
    guiEls.append(el)
    el.grid(row=indexEl, column=0)
    indexEl += 1
    updateScrollRegion()

def openImg(path):
    global imagesSizes
    image = Image.open(path)
    imagesSizes.append(tuple((image.width, image.height)))
    image = image.reduce(2)
    return image

def ImgToLabel(img):
    global listImagesLoaded
    img = ImageTk.PhotoImage(img)
    listImagesLoaded.append(img)
    l = Label(fTable, image=img)
    return l

def loadLogo():
    global logo, logoEl, logoMini
    file =  filedialog.askopenfilename(initialdir = "/",title = "Select PNG 4K file")
    if file == "":
        return
    logo = Image.open(file)
    logoMini = ImageTk.PhotoImage(logo.reduce(24))
    logoEl.configure(image=logoMini)

def clearGui():
    global listImagesLoaded, guiEls, imagesSizes, imagesExportReady, listPathImages, imagesCropped, listImagesGUICrop
    for el in guiEls:
        el.destroy()
    listImagesLoaded = []
    imagesSizes = []
    listImagesGUICrop = []
    imagesCropped = [None] * len(listPathImages)
    imagesExportReady = [None] * len(listPathImages)

def chooseFolder():
    root =  filedialog.askdirectory(initialdir = "/",title = "Select folder")
    print (root)
    if root != "": 
        findFiles(root)

def findFiles(path):
    result = glob.glob(path +"/drawable*/*.png", recursive=True)
    global listPathImages, imagesCropped
    listPathImages = result
    updateGui()

def shortenPath(path):
    p = path.replace("\\", "/")
    return re.search("/([^/]+)/([^/]+)/([^/]+)/?$", p)[0]

def cropAllImages():
    global listImagesGUICrop
    print(len(listImagesGUICrop))
    if len(listImagesGUICrop) < 0:
        return
    for i in range(len(listImagesGUICrop)):
        cropImage(i)

def cropImage(index):
    global listImagesLoaded, imagesCropped, listImagesGUICrop, logo, logoMini, imagesSizes, imagesExportReady
    if len(listImagesGUICrop) < 0:
        return
    imgRes = crop(logo, imagesSizes[index])
    imagesExportReady[index] = imgRes
    imgRes = imgRes.reduce(2)
    img = ImageTk.PhotoImage(imgRes)
    imagesCropped[index] = img
    listImagesGUICrop[index].configure(image = img)

def crop(source, sizes): 
    print("cropping " + str(sizes))
    minSize = min(sizes[0], sizes[1])
    bgColor = source.getpixel((0, int(source.width/2.0)))
    sizes = tuple(sizes)
    x1, y1, x2, y2 = 0, 0, sizes[0], sizes[1]
    finalImg = source.resize((minSize, minSize))
    newImage = Image.new(exportedImagesBitDepth, (x2 - x1, y2 - y1), bgColor)
    xCenter = (sizes[0]/2.0) - (minSize/2.0)
    yCenter = (sizes[1]/2.0) - (minSize/2.0)
    newImage.paste(finalImg, (int(xCenter), int(yCenter)))
    return newImage

def undoCrop(index):
    listImagesGUICrop[index].configure(image = listImagesLoaded[index])
    imagesExportReady[index] = None

def overrideImages():
    for i in range(len(listPathImages)):
        if imagesExportReady[i] != None:
            imagesExportReady[i].save(listPathImages[i])

cButtonsContainer = Canvas(ws)
buttons_frame = Frame(cButtonsContainer)
buttons_frame.grid(column=0, row=2, sticky="N")
Button( buttons_frame, text ="Load images (select main/res folder)", command = chooseFolder).grid(column=0, row=0, sticky="N")
Button( buttons_frame, text ="Load a 4k(4096px) logo", command = loadLogo).grid(column=1, row=0, sticky="N")
Button( buttons_frame, text ="Crop all images", command = cropAllImages).grid(column=2, row=0, sticky="N")
logoEl = Label( buttons_frame, image="")
logoEl.grid(column=2, row=1, sticky="N")
Button( buttons_frame, text ="Save and OVERRIDE", command = overrideImages).grid(column=3, row=0, sticky="N")
cButtonsContainer.pack(fill=BOTH, side=TOP, expand=FALSE)
createScrollableContainer()

ws.mainloop()