import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader
from PIL import Image, ImageTk
import fitz
import os

listaImagenes = []
ct = 1
cbab = 1 #contador botones de acción
cbabC = 1
contadorImagenes = 0
imagenesFrm = None
imgTemSelec = None
imgTemSelected = []
nombreArchivo = ''
rutaArchivo = ''
archivosCompressSelected = None

def convertir_tiff_a_grises_y_comprimir(ruta_entrada, ruta_salida, calidad=10):
    # Abrir el archivo multi-TIFF
    img = Image.open(ruta_entrada)
    
    # Lista para almacenar las páginas procesadas
    paginas_grises = []

    for i in range(img.n_frames):
        # Seleccionar la página
        img.seek(i)
        
        # Convertir a escala de grises
        pagina_grises = img.convert("L")
        
        # Añadir la página a la lista
        paginas_grises.append(pagina_grises)

    # Guardar el nuevo archivo TIFF en escala de grises y comprimido
    if paginas_grises:
        paginas_grises[0].save(
            ruta_salida,
            save_all=True,
            append_images=paginas_grises[1:],
            compression="tiff_jpeg",
            quality=calidad
        )

        paginas_grises[0].save(
            f"imagenes/{os.path.basename(ruta_salida)}",
            save_all=True,
            append_images=paginas_grises[1:],
            compression="tiff_jpeg",
            quality=calidad
        )
    print("comprimido")


def seleccionarArchivosCompresion():
    global archivosCompressSelected, cbabC
    try:
        imagenesFrm.destroy()
        #frame_principal.destroy()
        funcionesImg.destroy()
        imagenesFrm.destroy()
        pass
    except:
        pass
   
    archivos_tiff = filedialog.askopenfilenames(filetypes=[("Archivos TIFF", ["*.tiff", "*.tif"])])

    if (archivos_tiff and cbabC == 1):
        compressImagesView.pack()

        textDpiSeleccionadoCompress = tk.Label(compressImagesView, text='DPI')
        dpiSeleccionadoCompress = tk.Entry(compressImagesView, textvariable=dpiSeleccionadoCV)
        textAlert =  tk.Label(compressImagesView, textvariable=alertC)
        buttonCompress = tk.Button(compressImagesView, text='Comprimir', bg='blue', fg='white', command=procesarCompressionP)

        textAlert.pack(padx=10, pady=10)
        textDpiSeleccionadoCompress.pack(padx=10, pady=10)
        dpiSeleccionadoCompress.pack(padx=10, pady=10)
        buttonCompress.pack(padx=10, pady=10)

        dpiSeleccionadoCV.set('70')
        #dpiSeleccionadoCV.config(text=dpiSeleccionadoCV.cget("text"))

        #for archivo in archivos_tiff:
        #    convertir_tiff_a_grises_y_comprimir(archivo, archivo, calidad=30)
        cbabC = cbabC + 1
    archivosCompressSelected = archivos_tiff
    return archivos_tiff

def procesarCompressionP():
    for archivoC in archivosCompressSelected:
        convertir_tiff_a_grises_y_comprimir(archivoC, archivoC, calidad=int(dpiSeleccionadoCV.get()))
        convertir_tiff_a_grises_y_comprimir(archivoC, archivoC, calidad=int(dpiSeleccionadoCV.get()))
    try:
        alertC.set('Comprimido')
    except:
        pass
def avanzarImagen():
    global imagenesFrm, contadorImagenes
    try:
        if (contadorImagenes < (len(listaImagenes)-1)):
            imagenesFrm.destroy()
            imagenesFrm = tk.Frame(app)
            imagenesFrm.pack()
            mostrarImagen(listaImagenes[contadorImagenes+1])
            contadorImagenes = contadorImagenes + 1
            etiqueta_archivo["text"] =  f"Nombre de página: --- >  {imgTemSelec}".replace('temp/', '').replace('.png', '')
    except ValueError as e:
        print(e)

def retrocederImagen():
    global imagenesFrm, contadorImagenes
    try:
        if (contadorImagenes > 0):
            imagenesFrm.destroy()
            imagenesFrm = tk.Frame(app)
            imagenesFrm.pack()
            mostrarImagen(listaImagenes[contadorImagenes - 1])
            contadorImagenes = contadorImagenes - 1
            etiqueta_archivo["text"] =  f"Nombre de página: --- >  {imgTemSelec}".replace('temp/', '').replace('.png', '')
    except ValueError as e:
        print(e)

def convertirPdfImagenes():
    rf = seleccionar_archivo()
    convertir_pdf_a_imagenes(rf, 'temp')
    #convertir_a_multi_tiff(listaImagenes, 'imagenes/salida.tiff')
    mostrarImagen(listaImagenes[contadorImagenes])

def procesarCambioPdfTiff():
    global imgTemSelected
    print("largo seleccionado " + str(len(imgTemSelected)))
    print(imgTemSelected)
    if (len(imgTemSelected) != 0):
        convertir_pdf_a_imagenes(rutaArchivo, 'temp', int(dpiSeleccionado.get()))
        convertir_a_multi_tiff(imgTemSelected, f'imagenes/{nombreArchivo}.tiff'.replace('.pdf', ''))
    else:
        convertir_pdf_a_imagenes(rutaArchivo, 'temp', int(dpiSeleccionado.get()))
        convertir_a_multi_tiff(listaImagenes, f'imagenes/{nombreArchivo}.tiff'.replace('.pdf', ''))
        


    li.set('Archivo .tiff creado')
    lblImgS.config(text=lblImgS.cget("text"))
    imgTemSelected = []

def seleccionar_archivo():
    global imagenesFrm, listaImagenes, contadorImagenes, imgTemSelec, imgTemSelected, dpiSeleccionado, rutaArchivo
    dpiSeleccionado.set('75')
    imgTemSelected = []
    contadorImagenes = 0

    archivo = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
    # Aquí puedes hacer algo con el nombre del archivo seleccionado, como mostrarlo en una etiqueta
    etiqueta_archivo["text"] = 'Ruta: ' + archivo + f" - page_1"

    try:
        imagenesFrm.destroy()
        imagenesFrm = tk.Frame(app)
        imagenesFrm.pack()
        listaImagenes = []
        imgTemSelec = []
        imagenesSeleccionadas()
        rutaArchivo = archivo
    except ValueError as e:
        print(e)
    return archivo



def convertir_pdf_a_imagenes(pdf_path, output_folder='output', dpi=200):
    global nombreArchivo
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Abrir el PDF
    doc = fitz.open(pdf_path)
    
    # Recorrer cada página del PDF
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Cargar la página
        mat = fitz.Matrix(dpi / 72, dpi / 72)  # Ajuste de DPI (resolución)
        pix = page.get_pixmap(matrix=mat)  # Convertir página a imagen

        # Guardar la imagen
        output_filename = os.path.join(output_folder, f'page_{page_num + 1}.png')
        pix.save(output_filename)
        listaImagenes.append(f'temp/page_{page_num + 1}.png')
        print(f"Imagen guardada: {output_filename}")

    print("Conversión PDF a PNG completada")
    nombreArchivo = os.path.basename(pdf_path)

def convertir_a_multi_tiff(lista_imagenes, output_path):
    global dpiSeleccionadoCV, archivosCompressSelected
    lista_imagenes_SD = []

    for ix in lista_imagenes:
        if ix not in lista_imagenes_SD:
            lista_imagenes_SD.append(ix)

    lista_imagenes = lista_imagenes_SD

    if not lista_imagenes:
        raise ValueError("La lista de imágenes está vacía.")

    # Abrir la primera imagen
    imagen_principal = Image.open(lista_imagenes[0])

    # Convertir las demás imágenes a objetos Image
    imagenes_secundarias = []
    for imagen_path in lista_imagenes[1:]:
        img = Image.open(imagen_path)
        imagenes_secundarias.append(img)

    # Guardar como un archivo multi-TIFF
    imagen_principal.save(
        output_path,
        save_all=True,
        append_images=imagenes_secundarias,
        compression="tiff_jpeg",
        quality=30
    )

    print(f"Archivo multi-TIFF guardado en: {output_path}")
    archivosCompressSelected = []
    archivosCompressSelected.append(output_path)
    dpiSeleccionadoCV = dpiSeleccionado
    #print(archivosCompressSelected)
    procesarCompressionP()
    print("Compresión adicional aplicada")


#listaImagenes = []
#listaImagenes.append('C:/Users/stive/OneDrive/ENTREGA DOCUMENTOS SENA/CC - 1022322859.pdf')
#convertir_a_multi_tiff(['C:/Users/stive/OneDrive/ENTREGA DOCUMENTOS SENA/CC - 1022322859.pdf'], 'C:/Users/stive/OneDrive/ENTREGA DOCUMENTOS SENA/CC - 1022322859.pdf')

def imagenesSeleccionadas():
    global imgTemSelec, imgTemSelected
    #print(f"este es{imgTemSelec}")

    tmplist = 'Imagenes seleccionadas ----> '
    tempImgTemSelected = []
    imgTemSelected.append(imgTemSelec)
    for i in imgTemSelected:
        if i not in tempImgTemSelected and i != []:
            tempImgTemSelected.append(i)

    imgTemSelected = tempImgTemSelected
    for i2 in tempImgTemSelected:
        tmplist = tmplist + f"{i2}, ".replace('temp/', '').replace('.png', '')

    li.set(str(tmplist))
    lblImgS.config(text=lblImgS.cget("text"))
    print(imgTemSelected)

def crearBotonesAcciones():
    global cbab, imgTemSelec

    #if (lblImgS.winfo_ismapped() == False):
    lblImgS.pack()
 
    if (cbab == 1):
        # Botones de acciones
        retroceder = tk.Button(funcionesImg, text="Retroceder", command=retrocederImagen)
        avanzar = tk.Button(funcionesImg, text="Avanzar", command=avanzarImagen)
        seleccionar = tk.Button(funcionesImg, text="Seleccionar", command=imagenesSeleccionadas)
        textDpiSelec = tk.Label(funcionesImg, text='DPI')
        dpiSelect = tk.Entry(funcionesImg, textvariable=dpiSeleccionado)
        procesar = tk.Button(funcionesImg, text="Convertir PDF", bg='blue', fg='white', command=procesarCambioPdfTiff)


        retroceder.pack(side=tk.LEFT, padx=10, pady=10)
        avanzar.pack(side=tk.LEFT, padx=10, pady=10)
        seleccionar.pack(side=tk.LEFT, padx=10, pady=10)
        textDpiSelec.pack(side=tk.LEFT, padx=5, pady=10)
        dpiSelect.pack(side=tk.LEFT, padx=10, pady=10)
        procesar.pack(side=tk.LEFT, padx=10, pady=10)

    cbab = cbab+1

def mostrarImagen(i):
    global cbab, imgTemSelec

    #if (lblImgS.winfo_ismapped() == False):
    lblImgS.pack()
    crearBotonesAcciones()

    # Imagenes seleccionadas
    tk.Label(
        imagenesSelect,
        text='Imagen'
    )

    imagen = Image.open(i)

    nuevo_ancho = 1000  # Nuevo ancho deseado
    nuevo_alto = 1200  # Nuevo alto deseado
    imagen_redimensionada = imagen.resize((nuevo_ancho, nuevo_alto))

  

    # Convertir a PhotoImage
    imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)

    # Crear un Frame para el Canvas y las barras de desplazamiento
    frame_principal = tk.Frame(imagenesFrm)
    frame_principal.pack(fill=tk.BOTH, expand=True)

    # Crear el Canvas dentro del Frame
    canvas = tk.Canvas(frame_principal, width=1200, height=1200)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Agregar barras de desplazamiento al Frame
    scrollbar_y = tk.Scrollbar(frame_principal, orient=tk.VERTICAL, command=canvas.yview, width=30)
    scrollbar_y.pack(side=tk.LEFT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = tk.Scrollbar(frame_principal, orient=tk.HORIZONTAL, command=canvas.xview)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Crear un Frame dentro del Canvas para contener la imagen
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')
    #canvas.place(relx=1, rely=1, anchor="center")

    # Mostrar la imagen en el Frame
    label = tk.Label(frame, image=imagen_tk)
    label.pack(
        #fill=tk.BOTH,
        padx=20,
        pady=20
    )

    # Mantener una referencia a la imagen
    label.config(image=imagen_tk)
    label.image = imagen_tk  # Mantener la referencia a la imagen

    # Configurar el scrollregion para el canvas
    canvas.update_idletasks()  # Asegúrate de que el canvas esté actualizado
    canvas.config(scrollregion=canvas.bbox("all"))

    # Configurar las barras de desplazamiento
    scrollbar_y.config(command=canvas.yview)
    scrollbar_x.config(command=canvas.xview)
    
    imgTemSelec = i
    #imagenesSeleccionadas()


def cambiarImagen():
    label.destroy()

## ----------------------------------------
## INTERFAZ
## ----------------------------------------

app = tk.Tk()
#app.configure(background='black')
app.title('Conversión de archivos')
app.geometry('700x600')

##tk.Label(
##    app,
##    text='Seleccione el archivo y seleccione las imagenes a comprimir en el archivo .tiff',
##    justify='center',
##    font=('Arial', 12, 'bold'),
##    #bg='gray',
##    #fg='white'
##).pack(
##    padx=20,
##    pady=10
##)

boton_seleccionar = tk.Button(
    app,
    text="Convertir archivo PDF a multi-tiff comprimido",
    bg='black',
    fg='white',
    font=('Arial', 12, 'bold'),
    command=convertirPdfImagenes
).pack(
    fill=tk.BOTH,
    padx=20,
    pady=5
)

boton_seleccionar2 = tk.Button(
    app,
    text="Comprimir imagenes",
    bg='gray',
    fg='black',
    font=('Arial', 12, 'bold'),
    command=seleccionarArchivosCompresion
).pack(
    fill=tk.BOTH,
    padx=20,
    pady=5
)



imagenesSelect = tk.Frame(app)

imgsS = tk.StringVar(imagenesSelect)
li = tk.StringVar(imagenesSelect)

lblImgS = tk.Label(
    imagenesSelect,
    textvariable=li,
    font=("Arial", 12, "bold")
)

funcionesImg = tk.Frame(
    app
)

dpiSeleccionado = tk.StringVar(funcionesImg)

funcionesImg.pack(pady=20)
etiqueta_archivo = tk.Label(app, text="")
etiqueta_archivo.pack()
imagenesSelect.pack(pady=20)

imagenesFrm = tk.Frame(app)
imagenesFrm.pack()

compressImagesView = tk.Frame(app)
dpiSeleccionadoCV = tk.StringVar(compressImagesView)
alertC = tk.StringVar(compressImagesView)

app.mainloop()