from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from flask import Flask, request
from flask_cors import CORS



def verifyCredentials():
    pass


def logindrive():
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # Abre un navegador para la autenticación
        ### USAR SELENIUM
        drive = GoogleDrive(gauth)
        ### SAVE CREDENTIALS
        # with open('credenciales.pickle', 'wb') as archivo:
        #     pickle.dump(drive, archivo)
        # Obtener el correo del usuario
        return drive

def loadCredentials():
    pass

def getFiles():
    pass

def uploadfile(drive,name,folder_id):
    file = drive.CreateFile({'title': name, 'parents': [{'id': folder_id}], 'access_level': 'public'})
    file.SetContentFile(name)  # Reemplaza con la ruta de tu imagen local
    file.Upload()
    file.InsertPermission({
    'type': 'anyone',
    'value': 'anyone',
    'role': 'reader'
    })

def createCarpet(drive):
    # Crear una carpeta en el Drive del usuario
    folder_metadata = {
        'title': 'Inference',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()

    return folder['id']

def getCarpets(drive):
    carpetas = []
    # Realizar la consulta para obtener las carpetas
    folder_list = drive.ListFile({'q': "mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
    
    # Recorrer la lista de carpetas
    for folder in folder_list:
        # Imprimir nombres de las carpetas
        if(folder['title'] == 'Inference'):
            # carpet = {'title':folder['title'],'ID':folder['id']}
            # Almacenar los nombres de las carpetas en la lista
            carpetas.append(folder['id'])

    # Imprimir la lista de nombres de carpetas
    return carpetas

def getFilesCarpet(drive,carpet_id):
    # ID de la carpeta de la que deseas obtener los archivos (reemplaza 'ID_DE_LA_CARPETA' con el ID de la carpeta específica)
    folder_id = carpet_id
    files = []
    # Consultar los archivos en la carpeta específica
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    # Recorrer y mostrar los archivos
    for file in file_list:
        files.append({'Nombre': file['title'], 'ID':file['id'],'Link':f"https://drive.google.com/uc?id={file['id']}"})
    return files

#### CREAMOS UNA CLASE PARA CONTROLAR EL SERVICIO ####


class DriveControl():
    
    def startDrive(self):
        ### INICIAMOS SESIÓN LOGIN
        self.drive = logindrive()

    def defineCarpet(self):
        #### CREAMOS O CARGAMOS EL ID DE LA CARPETA
        Carpets = getCarpets(self.drive)
        if(len(Carpets) == 0):
            self.CreateCarpet() ## SI NO HAY CARPETA LA CREAMOS Y GUARDAMOS EL ID
        else:
            self.carpet_id = Carpets[0] ### GUARDAMOS EL ID
    
    def getFileCarpet(self):
        ### OBTENEMOS LOS ARCHIVOS DE LA CARPETA
        list_files = getFilesCarpet(self.drive,self.carpet_id)
        return list_files
    


    def CreateCarpet(self):
        self.carpet_id = createCarpet(self.drive)


    def uploadFile(self,name):
        #### SUBIMOS EL ARCHIVO
        uploadfile(self.drive,name,self.carpet_id)

### CREAMOS LA CLASE
app = Flask(__name__)
CORS(app)

drive_control = DriveControl() 

@app.route('/login', methods=['GET'])
def login():
    drive_control.startDrive()
    drive_control.defineCarpet()
    return {'status':'Sesión iniciada correctamente'}


@app.route('/getFiles', methods=['GET'])
def getFiles():
    return drive_control.getFileCarpet()



@app.route('/uploadFiles', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return 'No se encontró el archivo en la solicitud'

#     file = request.files['file']
#     if file.filename == '':
#         return 'Archivo no seleccionado'

#     # Guardar el archivo en el servidor (por ejemplo, en la carpeta 'uploads')
#     file.save('uploads/' + file.filename)
    
#     return {'status':'Archivo subido exitosamente'}

def uploadFile():

     file = request.files['file']
     name = request.form.get('name')
     print("FILE: ",file,name)
     ### GUARDAMOS EL ARCHIVO 
     nombre_archivo_guardado = name

     # Abre el archivo en modo escritura y escribe el contenido del objeto file
     with open(nombre_archivo_guardado, 'wb') as nuevo_archivo:
        # Lee y escribe el contenido del objeto file en el nuevo archivo
        nuevo_archivo.write(file.read())

     print(f'Archivo guardado exitosamente como {nombre_archivo_guardado}')

     drive_control.uploadFile(name)

     return {'status':'subido correctamente'}
    



    

if __name__=='__main__':

    app.run(host='0.0.0.0', port=5000)
    #getAuthDrive('jumendezro@unal.edu.co') ## obtenemos las credenciales
    #drive = logindrive()
    #createCarpet(drive)## creamos la carpeta y obtenemos el id de esa carpeta
    #getCarpets(drive)
    #getFilesCarpet(drive)
    #uploadFile(drive)
