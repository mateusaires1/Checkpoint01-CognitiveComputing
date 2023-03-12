import cv2
import numpy as np
import math
import pynput
from pynput.keyboard import Controller
from pynput.keyboard import Key
import time

# video com a exemplo: https://youtu.be/flEMW3K7tvs #

# amarelo
amarelo_lower_hsv = (22, 93, 0)
amarelo_upper_hsv = (45, 255, 255)

# vermelho
vermelho_lower_hsv = (0,50,50)
vermelho_upper_hsv = (10,255,255)

# mascaras #
def CONVERTE_BRG2HSV(img_bgr, low_hsv, high_hsv):
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img, low_hsv, high_hsv)
    return mask

def mascara_or(mask1, mask2):
    mask = cv2.bitwise_or(mask1, mask2)
    return mask

def mascara_and(mask1, mask2):
    mask = cv2.bitwise_and(mask1, mask2)

    return mask
# fim mascaras #

# funcao cruz no centros dos circulos #
def cruz_no_centro(img, cX, cY, size, color):
    cv2.line(img, (cX - size, cY), (cX + size, cY), color, 5)
    cv2.line(img, (cX, cY - size), (cX, cY + size), color, 5)

# fim funcao cruz no centros dos circulos #

# definicao do controle para pular #
def controls(angle, area):
    keyboard = Controller()
    if angle > 270 and angle < 340:
        keyboard.press(Key.space)
        time.sleep(0.1)
# fim definicao do controle para pular #


# imagem da webcam (aplicação das mascaras, contornos e reta) #
def image_da_webcam(img):
    contornos_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask_amarelo = cv2.inRange(contornos_img, amarelo_lower_hsv, amarelo_upper_hsv)
    mask_amarelo = cv2.erode(mask_amarelo, None, iterations=2)
    mask_amarelo = cv2.dilate(mask_amarelo, None, iterations=2)

    mask_vermelho = cv2.inRange(contornos_img, vermelho_lower_hsv, vermelho_upper_hsv)
    mask_vermelho = cv2.erode(mask_vermelho, None, iterations=2)
    mask_vermelho = cv2.dilate(mask_vermelho, None, iterations=2)

    contorno_amarelo = cv2.findContours(mask_amarelo.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    centerGreen = None
    contorno_vermelho = cv2.findContours(mask_vermelho.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    centerYellow = None

    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    area1 = 0
    area2 = 0

    if len(contorno_amarelo) > 0:
        cAmarelo = max(contorno_amarelo, key=cv2.contourArea)
        MAmarelo = cv2.moments(cAmarelo)
        if MAmarelo["m00"] != 0:
            x1 = int(MAmarelo["m10"] / MAmarelo["m00"])
            y1 = int(MAmarelo["m01"] / MAmarelo["m00"])
        rectAmarelo = cv2.minAreaRect(cAmarelo)
        boxAmarelo = cv2.boxPoints(rectAmarelo)
        boxAmarelo = np.int0(boxAmarelo)
        centerAmarelo = (x1, y1)
        cv2.drawContours(contornos_img, [boxAmarelo], 0, (0, 255, 0), 2)
        cruz_no_centro(contornos_img, x1, y1, 20, (0, 255, 0))
        area1 = cv2.contourArea(cAmarelo)

    if len(contorno_vermelho) > 0:
        cVermelho = max(contorno_vermelho, key=cv2.contourArea)
        MVermelho = cv2.moments(cVermelho)
        if MVermelho["m00"] != 0:
            x2 = int(MVermelho["m10"] / MVermelho["m00"])
            y2 = int(MVermelho["m01"] / MVermelho["m00"])
        rectVermelho = cv2.minAreaRect(cVermelho)
        boxVermelho = cv2.boxPoints(rectVermelho)
        boxVermelho = np.int0(boxVermelho)
        centerVermelho = (x2, y2)
        cv2.drawContours(contornos_img, [boxVermelho], 0, (0, 255, 255), 2)
        cruz_no_centro(contornos_img, x2, y2, 20, (0, 255, 255))
        area2 = cv2.contourArea(cVermelho)

# Desenha a linha ligando os circulos #
    color = (255, 255, 255)
    cv2.line(contornos_img, (x1, y1), (x2, y2), color, 5)
# fim desenha a linha ligando os circulos #

    vY = y1 - y2
    vX = x1 - x2
    rad = math.atan2(vY, vX)
    angulo = math.degrees(rad)
    if angulo < 0:
        angulo += 360
    mediaArea = (area1 + area2) / 2
    controls(angulo, mediaArea)
    origem = (0, 100)
    contornos_img2 = cv2.cvtColor(contornos_img, cv2.COLOR_HSV2BGR)
    return contornos_img2

                                                                    
######## WEB CAM #########

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

vc.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if vc.isOpened():  # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:

    img = image_da_webcam(frame) 

    cv2.imshow("preview", img)
    # cv2.imshow("original", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()
