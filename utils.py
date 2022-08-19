import cv2

class VideoCamera():
    def __init__(self, id:int):
        print(f'camera id: {id}')
        self.video = cv2.VideoCapture(id)
        if id > 1:
            self.video.set(cv2.CAP_PROP_FPS, 30.0)
            self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
            self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
            self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        retain, image = self.video.read()
        if retain:
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
      