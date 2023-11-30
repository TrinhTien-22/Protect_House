from flask import Flask, render_template, request, session, redirect, url_for, Response, jsonify
# from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
# from werkzeug.urls import url_unquote
from flask_socketio import SocketIO
import mysql.connector
import cv2
from PIL import Image 
import numpy as np
import os
import time
from datetime import date
import threading
import json
# import cv2
# import pyfirmata
# from cvzone.HandTrackingModule import HandDetector
# from cvzone.FPS import FPS

from cvzone.HandTrackingModule import HandDetector
import paho.mqtt.client as mqtt
# import cv2.dnn
app = Flask(__name__)
socketio = SocketIO(app)
 
cnt = 0
pause_cnt = 0
justscanned = False 
camera_running = True
lastdata = ""
newdata = ""
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="flask_db"
)
mycursor = mydb.cursor()
mqtt_client = mqtt.Client()

mqtt_client.connect("192.168.0.109", 1883)

mqtt_client.subscribe("livingroom")
mqtt_client.loop_start()

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Generate dataset >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def generate_dataset(nbr):
    face_classifier = cv2.CascadeClassifier(r'C:\Users\Admin\Documents\live_face_recognition\resources\haarcascade_frontalface_default.xml')
 
    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        # scaling factor=1.3
        # Minimum neighbor = 5
 
        if faces is ():
            return None
        for (x, y, w, h) in faces:
            cropped_face = img[y:y + h, x:x + w]
        return cropped_face
 
    cap = cv2.VideoCapture(0)
 
    mycursor.execute("select ifnull(max(img_id), 0) from img_dataset")
    row = mycursor.fetchone()
    
    lastid = row[0]
 
    img_id = lastid
    max_imgid = img_id + 100
    count_img = 0
 
    while True:
        ret, img = cap.read()
        if face_cropped(img) is not None:
            count_img += 1
            img_id += 1
            face = cv2.resize(face_cropped(img), (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
 
            file_name_path = "dataset/"+nbr+"."+ str(img_id) + ".jpg"
            cv2.imwrite(file_name_path, face)
            cv2.putText(face, str(count_img), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
 
            mycursor.execute("""INSERT INTO `img_dataset` (`img_id`, `img_person`) VALUES
                                ('{}', '{}')""".format(img_id, nbr))
            mydb.commit()
            
            frame = cv2.imencode('.jpg', face)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
 
            if cv2.waitKey(1) == 13 or int(img_id) == int(max_imgid):
                break
                cap.release()
                cv2.destroyAllWindows()
 
 
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Train Classifier >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route('/train_classifier/<nbr>')
def train_classifier(nbr): 
    dataset_dir = r'C:\Users\Admin\Documents\live_face_recognition\dataset'
 
    path = [os.path.join(dataset_dir, f) for f in os.listdir(dataset_dir)]
    faces = []
    ids = []
 
    for image in path:
        img = Image.open(image).convert('L');
        imageNp = np.array(img, 'uint8')
        id = int(os.path.split(image)[1].split(".")[1])
 
        faces.append(imageNp)
        ids.append(id)
    ids = np.array(ids)
 
    # Train the classifier and save
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write('classifier.xml')
 
 
    return redirect('/')
 
 
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Face Recognition >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def face_recognition():  # generate frame by frame from camera
    # broker = "192.168.0.109"
    topic = "Trinhtien22"
    # client = mqtt.Client()
    # client.connect(broker)
    def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf):
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = classifier.detectMultiScale(gray_image, scaleFactor, minNeighbors)
 
        global justscanned
        global pause_cnt
        global lastdata
        global newdata
        newdata = ""
        pause_cnt += 1
 
        coords = []
 
        for (x, y, w, h) in features:
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            id, pred = clf.predict(gray_image[y:y + h, x:x + w])
            confidence = int(100 * (1 - pred / 300))
 
            if confidence > 70 and not justscanned:
                
                # lastData = strVal
                global cnt
                
                cnt += 1
 
                n = (100 / 30) * cnt
                # w_filled = (n / 100) * w
                w_filled = (cnt / 30) * w
 
                cv2.putText(img, str(int(n))+' %', (x + 20, y + h + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (153, 255, 255), 2, cv2.LINE_AA)
 
                cv2.rectangle(img, (x, y + h + 40), (x + w, y + h + 50), color, 2)
                cv2.rectangle(img, (x, y + h + 40), (x + int(w_filled), y + h + 50), (153, 255, 255), cv2.FILLED)
 
                mycursor.execute("select a.img_person, b.prs_name, b.prs_skill "
                                 "  from img_dataset a "
                                 "  left join prs_mstr b on a.img_person = b.prs_nbr "
                                 " where img_id = " + str(id))
                row = mycursor.fetchone()
                
                pnbr = row[0]
                pname = row[1]
                pskill = row[2]

                def pubopendoor():
                    global newdata
                    newdata = ""

                if int(cnt) == 30:
                    cnt = 0
 
                    mycursor.execute("insert into accs_hist (accs_date, accs_prsn) values('"+str(date.today())+"', '" + pnbr + "')")
                    mydb.commit()
                    
                    cv2.putText(img, pname + ' | ' + pskill, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (153, 255, 255), 2, cv2.LINE_AA)
                    time.sleep(1)
 

                    justscanned = True
                    pause_cnt = 0
                    
                    thread = threading.Timer(5, pubopendoor)
                    thread.start()
                    lastdata = "opendoor "+ pname
                    if lastdata != newdata :
                        mqtt_client.publish(topic, "opendoor "+ pname)
                        print(f'Publish Message: {"opendoor " + pname}')
                        newdata = "opendoor "+ pname
                    
                    
            else:
                if not justscanned:
                    cv2.putText(img, 'UNKNOWN', (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    cv2.putText(img, ' ', (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2,cv2.LINE_AA)
 
                if pause_cnt > 80:
                    justscanned = False
 
            coords = [x, y, w, h]   
     
        return coords
 
    def recognize(img, clf, faceCascade):
        coords = draw_boundary(img, faceCascade, 1.1, 10, (255, 255, 0), "Face", clf)
        return img

 
 
    faceCascade = cv2.CascadeClassifier(r'C:\Users\Admin\Documents\live_face_recognition\resources\haarcascade_frontalface_default.xml')
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.read("classifier.xml")
 
    wCam, hCam = 400, 400
 
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
 
    while camera_running:
        ret, img = cap.read()
        img = recognize(img, clf, faceCascade)
 
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
       
        key = cv2.waitKey(1)
        if key == 32:
            break

# class User(UserMixin):
#     def __init__(self, id):
#         self.id = id

# @login_manager.user_loader
# def load_user(user_id):
#     return User(user_id)

#==========================================Login User================================================================
security = False
@app.route('/login', methods=['POST'])
def login():
    global security
    username = request.form.get('username') 
    mycursor.execute("SELECT prs_name FROM prs_mstr WHERE prs_name = %s", (username,))
    user = mycursor.fetchone()
    
    if user:
        security = True
        return redirect(url_for('livingroom'))
    else:
        return redirect(url_for('fr_page'))

#====================================================Update user============================================
@app.route('/member/update/<int:id>' , methods = ['GET'])
def memberupdate(id): 
    mycursor.execute("SELECT * FROM prs_mstr WHERE prs_nbr = %s", (id,))
    data = mycursor.fetchone()
    
    return jsonify({'respone' : data})
@app.route('/member/update/finish/<int:id>', methods=['POST'])
def memberupdatefinish(id):
    
    prsname = request.form.get('namemember')
    prsskill = request.form.get('membermember')
    prsavata = request.files['avataupdate']
    
    if prsavata:
        mycursor.execute("SELECT prs_avata FROM prs_mstr WHERE prs_nbr = %s", (id,))
        oldimgavata = mycursor.fetchone()[0]
        
        upload_folder = r'C:\Users\Admin\Documents\live_face_recognition\static\img\avata'
        file_path = os.path.join(upload_folder, oldimgavata)

        if os.path.exists(file_path):
            os.remove(file_path)

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file_path = os.path.join(upload_folder, prsavata.filename)
        prsavata.save(file_path)

        sql = "UPDATE prs_mstr SET prs_name = %s, prs_skill = %s, prs_avata = %s WHERE prs_nbr = %s"
        values = (prsname, prsskill, prsavata.filename, id)
        mycursor.execute(sql, values)
        mydb.commit()
        
        response_data = {"prsname": prsname, "prsskill": prsskill, "prsavata": prsavata.filename}
        return jsonify(response_data)
    else:
        sql = "UPDATE prs_mstr SET prs_name = %s, prs_skill = %s WHERE prs_nbr = %s"
        values = (prsname, prsskill, id)
        mycursor.execute(sql, values)
        mydb.commit()
        
        response_data = {"prsname": prsname, "prsskill": prsskill}
        return jsonify(response_data)


#=============================================Login Admin===========================================
admin = False
@app.route('/admin/login' , methods = ['POST'])
def adminlogin():
    email= request.form.get('emailadmin')
    password = request.form.get('passwordadmin')
    mycursor.execute(" select * from admin where id = %s" , (1,) )
    data = mycursor.fetchone()
    
    global admin 
    if email == data[1] and password == data[2] : 
        admin = True
        return jsonify('ok')
    else :
        return jsonify('not ok')

#================================================Delete User by Admin ======================================
def delete_user_images(user_id):
    dataset_folder = r'C:\Users\Admin\Documents\live_face_recognition\dataset'  # Đường dẫn đến thư mục dataset

    for filename in os.listdir(dataset_folder):
        if filename.startswith(f"{user_id}."):
            file_path = os.path.join(dataset_folder, filename)
            os.remove(file_path)

@app.route('/admin/deletemember/<int:id>' , methods = ['POST'])
def deletemember(id):
    mycursor.execute('select prs_avata from prs_mstr where prs_nbr = %s' , (id,))
    imgavata = mycursor.fetchone()[0]
    
    upload_folder = r'C:\Users\Admin\Documents\live_face_recognition\static\img\avata'
    
    file_path = os.path.join(upload_folder, imgavata)

    if os.path.exists(file_path):
        os.remove(file_path)

    mycursor.execute('delete from prs_mstr where prs_nbr=%s' , (id,))
    mycursor.execute('DELETE FROM img_dataset WHERE img_person = %s' , (id,))
    mydb.commit()
    
    delete_user_images(id)
    return jsonify("ok")

@app.route('/admin')
def admin():
    if admin == True:
        return render_template('admin.html')
    else:
        return redirect('/')

#===========================================Search User by Admin================================
@app.route('/admin/search/member' , methods = ['POST'])
def searching():
    keyword = request.form.get('keyword')
    mycursor.execute('select * from prs_mstr where prs_name like %s' , ('%' + keyword + '%',))
    data = mycursor.fetchall()
    
    return jsonify(data)


#=========================================== Home ========================================
@app.route('/')
def home():
    global camera_running
    camera_running = False
    # mycursor.execute("select prs_nbr, prs_name, prs_skill, prs_active, prs_added from prs_mstr")
    # data = mycursor.fetchall()
 
    return render_template('index.html' )

@app.route('/memberdata' , methods = ['GET'])
def memberdata():
    mycursor.execute("select * from prs_mstr")
    data = mycursor.fetchall()
    
    return jsonify({'response' : data})

#===========================================ADD Person===================================================
@app.route('/addprsn')
def addprsn():
    mycursor.execute("select ifnull(max(prs_nbr) + 1, 101) from prs_mstr")
    row = mycursor.fetchone()
    
    nbr = row[0]
    # print(int(nbr))
 
    return render_template('addprsn.html', newnbr=int(nbr))
 
@app.route('/addprsn_submit', methods=['POST'])
def addprsn_submit():
    prsnbr = request.form.get('txtnbr')
    prsname = request.form.get('txtname')
    prsskill = request.form.get('optskill')
    prsinterest = request.form.get('interest')
    prsavata = request.files['avata']

    upload_folder = r'C:\Users\Admin\Documents\live_face_recognition\static\img\avata'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, prsavata.filename)
    prsavata.save(file_path)
    mycursor.execute("""INSERT INTO `prs_mstr` (`prs_nbr`, `prs_name`, `prs_skill` ,`interest`, `prs_avata`) VALUES
                    ('{}', '{}', '{}' ,'{}' , '{}')""".format(prsnbr, prsname, prsskill ,prsinterest,prsavata.filename))
    mydb.commit()
    
    # return redirect(url_for('home'))
    return redirect(url_for('vfdataset_page', prs=prsnbr))
 
@app.route('/vfdataset_page/<prs>')
def vfdataset_page(prs):
    return render_template('gendataset.html', prs=prs)
 
@app.route('/vidfeed_dataset/<nbr>')
def vidfeed_dataset(nbr):
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(generate_dataset(nbr), mimetype='multipart/x-mixed-replace; boundary=frame')
 
 
@app.route('/video_feed')
def video_feed():
    global camera_running
    camera_running =True
    return Response(face_recognition(), mimetype='multipart/x-mixed-replace; boundary=frame')
 
@app.route('/fr_page')
def fr_page():
    """Video streaming home page."""
    mycursor.execute("select a.accs_id, a.accs_prsn, b.prs_name, b.prs_skill, a.accs_added "
                     "  from accs_hist a "
                     "  left join prs_mstr b on a.accs_prsn = b.prs_nbr "
                     " where a.accs_date = curdate() "
                     " order by 1 desc")
    data = mycursor.fetchall()
    
    return render_template('fr_page.html', data=data)
 
 
@app.route('/countTodayScan')
def countTodayScan():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="flask_db"
    )
    mycursor = mydb.cursor()
 
    mycursor.execute("select count(*) "
                     "  from accs_hist "
                     " where accs_date = curdate() ")
    row = mycursor.fetchone()
    
    rowcount = row[0]
 
    return jsonify({'rowcount': rowcount})
 
 
@app.route('/loadData', methods = ['GET', 'POST'])
def loadData():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="flask_db"
    )
    mycursor = mydb.cursor()
 
    mycursor.execute("select a.accs_id, a.accs_prsn, b.prs_name, b.prs_skill, date_format(a.accs_added, '%H:%i:%s') "
                     "  from accs_hist a "
                     "  left join prs_mstr b on a.accs_prsn = b.prs_nbr "
                     " where a.accs_date = curdate() "
                     " order by 1 desc"
                     " limit 1")
    data = mycursor.fetchone()
    
    return jsonify(response = data)


data_from_arduino = {}  # Lưu trữ dữ liệu từ Arduino
topic = "Warning"
current_value = 0
test = False
def warningmqtt():
    print("Sending warning message...")
    
    mqtt_client.publish(topic, "warning")
    print(f'Publish Message: {"warning"}') 

@app.route('/home/livingroom/warning', methods=['POST'])
def warning():
    global current_value
    global test
    data_type = request.form.get('dataType') 
    value = request.form.get(data_type) 

    update_query = "UPDATE warning SET {} = %s WHERE id = 1".format(data_type)
    mycursor.execute(update_query, (value,))
    mydb.commit()
    
    data = data_from_arduino
    
    if value != current_value:
        test = True
        current_value = value

    while test:
        newvalue = int(value)
        if data.get("Light", 0) > newvalue : 
            
            print(f'{value}')
            warningmqtt()
            time.sleep(10)  
        else:
            break
        if data.get("Temperature", 0) > newvalue : 
           
            print(f'{value}')
            warningmqtt()
            time.sleep(10)  
        else:
            break
        if data.get("Humidity", 0) > newvalue : 
            
            print(f'{value}')
            warningmqtt()
            time.sleep(10)  
        else:
            break
    test = False
    return Response("ok")

@app.route('/home/livingroom/getinforwarning', methods=['GET'])
def getinforwarning():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="flask_db"
    )
    mycursor = mydb.cursor()
    mycursor.execute('select * from warning where id = 1')
    data = mycursor.fetchone()
    return jsonify(data)

@app.route('/home/livingroom')
def livingroom():
    global security
    if security :
        return render_template('livingroom.html' )
    else :
        return redirect(url_for('fr_page'))
    
# temp = []
# humi = []
# light = []

# @app.route('/home/livingroom/data' , methods = ['GET'])
# def livingroomdata():
#     data=data_from_arduino
#     if len(temp) < 20 :
#         temp.push(data.Temperature)
#         humi.push(data.Humidity)
#         light.push(data.Light)
#     else:
#         for( i=0 , i<19 ; i++){
#             temp[i]=temp[i+1]
#             humi[i] = humi[i+1]
#             light[i] = light[i+1]
#         }
    
#     socketio.emit('send-data' , data)
#     return jsonify(Response = data)

# def on_message(client, userdata, message):
#     global data_from_arduino
#     data = message.payload.decode("utf-8")
#     data_from_arduino = json.loads(data)
# mqtt_client.on_message = on_message
temp = []
humi = []
light = []

@app.route('/home/livingroom/data', methods=['GET'])
def livingroomdata():
    global temp, humi, light, data_from_arduino
    data = data_from_arduino

    if len(temp) < 15:
        temp.append(data_from_arduino['Temperature'])
        humi.append(data_from_arduino['Humidity'])
        light.append(data_from_arduino['Light'])
    else:
        for i in range(12):
            temp[i] = temp[i+1]
            humi[i] = humi[i+1]
            light[i] = light[i+1]
        temp.pop(0)
        humi.pop(0)
        light.pop(0)

    socketio.emit('send-data-temp', temp)
    socketio.emit('send-data-humi', humi)
    socketio.emit('send-data-light', light)
    return jsonify(Response=data)

def on_message(client, userdata, message):
    global data_from_arduino
    data = message.payload.decode("utf-8")
    data_from_arduino = json.loads(data)

mqtt_client.on_message = on_message



def hand_tracking():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="flask_db"
    )
    mycursor = mydb.cursor()
    cap = cv2.VideoCapture(0)

    detector = HandDetector(detectionCon=1, maxHands=1)

    fingerTip = [4, 8, 12, 16, 20]
    fingerVal = [0, 0, 0, 0, 0]
    lastData = 00000

    red = (0,0,255)
    yellow = (0,255,255)
    blue = (255,0,0)
    green = (0,255,0)
    purple = (255,0,255)
    lastChangeTime = time.time()
    color = [red, yellow, blue, green, purple]

    # broker = "192.168.0.109"
    topic = "Trinhtien22"
    # client = mqtt.Client()
    # client.connect(broker)

    while cap.isOpened():
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img, draw=False)

        if lmList:
            # Thumb
            handType = detector.handType()
            if handType == "Right":
                if lmList[fingerTip[0]][0] > lmList[fingerTip[0]-1][0]:
                    fingerVal[0] = 1
                else:
                    fingerVal[0] = 0
            else:
                if lmList[fingerTip[0]][0] < lmList[fingerTip[0]-1][0]:
                    fingerVal[0] = 1
                else:
                    fingerVal[0] = 0

            #4 fingers
            for i in range(1,5):
                if lmList[fingerTip[i]][1] < lmList[fingerTip[i]-2][1]:
                    fingerVal[i] = 1
                else:
                    fingerVal[i] = 0

            #Draw mark
            for i in range(0,5):
                if fingerVal[i] == 1:
                    cv2.circle(img, (lmList[fingerTip[i]][0], lmList[fingerTip[i]][1]), 15,
                            color[i], cv2.FILLED)

            strVal = str(fingerVal[0])+str(fingerVal[1])+str(fingerVal[2])+str(fingerVal[3])+str(fingerVal[4])

            if lastData != strVal and time.time() - lastChangeTime >= 3:
                if strVal == '11111' or  strVal == '00000' or strVal=='01110' or strVal=='01100' or strVal=='01000' or strVal =='10001':
                    mycursor.execute('INSERT INTO activity (action) VALUES (%s)', (strVal,))
                    mydb.commit()
                    
                mqtt_client.publish(topic, strVal)
                print(f'Publish Message: {strVal}')
                lastData = strVal
                lastChangeTime = time.time()

        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        
    wCam, hCam = 400, 400
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    # video.release() 
    cv2.destroyAllWindows()
    

@app.route('/hand_track')
def hand_track():
    global camera_running
    camera_running =False
    return Response(hand_tracking(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/controlhome/get')
def controlget():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="flask_db"
    )
    mycursor = mydb.cursor()
    mycursor.execute('select * from activity order by create_at desc limit 5')
    data = mycursor.fetchall()
    return jsonify(data)
@app.route('/controlhome')
def controlhome():
    global security
    if security :
        return render_template('controlhome.html')
    else :
        return redirect(url_for('fr_page'))
    
 
if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=5000, debug=True)
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
