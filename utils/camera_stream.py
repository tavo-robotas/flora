from datetime import datetime
import cv2
import os

class VideoCamera():
    def __init__(self, id:int):
        print(f'camera id: {id}')
        self.video = cv2.VideoCapture(id)
        #if id > 1:
        self.video.set(cv2.CAP_PROP_FPS, 30.0)
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()

    def get_index(self):
        return 'id_0'

    def get_frame(self, save):
        retain, image = self.video.read()
        if retain:
            if datetime.now().strftime('%H-%M-%S') == '12-00-00':
                for i in range(1):
                    time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
                    f_name = os.path.join(f'{os.getcwd()}/assets/img/camera_captures/{self.get_index()}', time)
                    cv2.imwrite(f'{f_name}.png', image)
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()

def gen(camera, save:bool=False): 
    while True:
        frame = camera.get_frame(save)
        try:
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except TypeError as e:
            print(e)