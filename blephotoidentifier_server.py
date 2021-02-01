import flask
import werkzeug
import face_recognition
import cv2

app = flask.Flask(__name__)
nameList = []
matchList = []
encodingList = []
# Add names and photo locations of known encodings here
personDict = {
    "Barack Obama": "obama.jpg",
    "Joe Biden": "biden.jpg"
}
obama_image_file = personDict.get("Barack Obama")
biden_image_file = personDict.get("Joe Biden")
if obama_image_file != None:
    known_image = face_recognition.load_image_file(obama_image_file)
    face_locations = face_recognition.face_locations(known_image)
    print(face_locations)
    print(face_recognition.face_encodings(known_image)[0])
    encodingList.append([face_recognition.face_encodings(known_image)[0],"Barack Obama"])
else:
    encodingList.append([None,None])

if biden_image_file != None:
    known_image = face_recognition.load_image_file(biden_image_file)
    face_locations = face_recognition.face_locations(known_image)
    print(face_locations)
    print(face_recognition.face_encodings(known_image)[0])
    encodingList.append([face_recognition.face_encodings(known_image)[0],"Joe Biden"])
else:
    encodingList.append([None,None])

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    imagefile = flask.request.files['image']
    filename = werkzeug.utils.secure_filename(imagefile.filename)
    print("\nReceived image File name : " + imagefile.filename)
    imagefile.save(filename)
    img = cv2.imread(imagefile.filename)
    height, width = img.shape[0:2]
    rotationMatrix = cv2.getRotationMatrix2D((width/2, height/2), 270, 0.5)
    rotatedImage = cv2.warpAffine(img, rotationMatrix, (width,height))
    print(cv2.imwrite(imagefile.filename,rotatedImage))
    uploaded_image = face_recognition.load_image_file(imagefile.filename)
    image_encodings = face_recognition.face_encodings(uploaded_image)
    print(len(image_encodings))
    for index in range(len(image_encodings)):
        found = False
        unknown_encoding = image_encodings[index]
        for index2 in range(len(encodingList)):
            if encodingList[index2][0].all() != None:
                match = face_recognition.compare_faces([encodingList[index2][0]],unknown_encoding)
                if match[0]:
                    matchList.append(encodingList[index2][1])
                    print(encodingList[index2][1])
                    found = True
                    break
        if not found:
            matchList.append(None)
    orderedList = []
    for k in range(len(matchList)):
        if ((matchList[k] not in orderedList) | (matchList[k]==None)):
            if (matchList[k] == None):
                orderedList.append("None")
            else:
                orderedList.append(matchList[k])
    orderNames = "*".join(orderedList)
    print(orderNames)
    return orderNames

@app.route('/names', methods=['GET', 'POST'])
def get_names():
    names = flask.request.data
    namesStr = names.decode('utf-8')
    nameList = namesStr.split('*')
    print(nameList[0] + "h" + nameList[1])
    return "Name(s) Received"

app.run(host="0.0.0.0", port=5000, debug=True)