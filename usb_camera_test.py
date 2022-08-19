import cv2

camera = cv2.VideoCapture(3)

# camera.set(cv2.CAP_PROP_FPS, 30.0)
# camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
# camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
# camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if camera.isOpened():
    while True:
        retval, im = camera.read()
        print(im)

        k = cv2.waitKey(1) & 0xff == ord('q')
        if k == 27:
            break

camera.release()
cv2.destroyAllWindows()