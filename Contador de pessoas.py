import cv2
import PySimpleGUI as sg                        # Part 1 - The import

# Define the window's contents
layout = [  [sg.Text("lotacao maxima:")],[sg.Input()],
            [sg.Text("porcentagem maxima permitida:")],[sg.Input()],
            [sg.Text("pessoas dentro do estabelecimento:")],[sg.Input()],
            [sg.Button('Ok')] ]

# Create the window
window = sg.Window('Contagem Pessoas G4', layout)      # Part 3 - Window Defintion

# Display and interact with the Window
event, values = window.read()                   # Part 4 - Event loop or Window.read call

# Do something with the information gathered
a=int(values[0])
b=int(values[1])
c=int(values[2])
vmax=(a*b)/100


# Finish up by removing from the screen
window.close()                                  # Part 5 - Close the Window


def center(x, y, w, h):     #formula para definir centro da tela
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy


cap = cv2.VideoCapture('1.mp4') #captura video

fgbg = cv2.createBackgroundSubtractorMOG2() #criacao mascara para estracao do video

detects = []

posL = 150 #250 #150
offset = 30 #50 #30

xy1 = (20, posL) #200 #20
xy2 = (350, posL) #600 #350

total =c

up = 0
down = 0

while 1:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("gray", gray)

    fgmask = fgbg.apply(gray) #aplica mascara preto e branco
    # cv2.imshow("fgmask", fgmask)

    retval, th = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY) #aplica a mascara #200 vai retirar manchas do video#255 claridade, conversao pra preto e branco
    # cv2.imshow("th", th)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) #aplica estrutura pra preencher a imagem com 'quadrados'

    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=2) #remove pontos aleatorios ao redor da massa
    # cv2.imshow("opening", opening)

    dilation = cv2.dilate(opening, kernel, iterations=8) #preencher os espacos vazios na massa entre os quadrados
    # cv2.imshow("dilation", dilation)

    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel, iterations=8) #imagem final com todas variaveis
    cv2.imshow("closing", closing)

    cv2.line(frame, xy1, xy2, (255, 0, 0), 2) #criacao linha centro

    cv2.line(frame, (xy1[0], posL - offset), (xy2[0], posL - offset), (255, 255, 0), 2) # criacao linha pra baixo

    cv2.line(frame, (xy1[0], posL + offset), (xy2[0], posL + offset), (255, 255, 0), 2) # criacao linha pra cima

    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # contorno do closing
    i = 0
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt) #funcao retangulo

        area = cv2.contourArea(cnt)#area de contorno

        if int(area) > 2000:#area deteccao centro da linha
            centro = center(x, y, w, h)

            cv2.putText(frame, str(i), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)#adiciona numero identificando quantos objetos estao no video ao mesmo tempo
            cv2.circle(frame, centro, 4, (255, 0, 0), -1)#circulo centro do retangulo
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3) #cria retangulo em volta do contorno
            if len(detects) <= i:
                detects.append([])#append(matriz dentro da lista) lista detectacao
            if centro[1] > posL - offset and centro[1] < posL + offset:
                detects[i].append(centro)
            else:
                detects[i].clear()
            i += 1

    if i == 0:
        detects.clear()#imagem vazia pega detects e esvazia a lista

    i = 0

    if len(contours) == 0:
        detects.clear()

    else:

        for detect in detects:
            for (c, l) in enumerate(detect):

                if detect[c - 1][1] < posL and l[1] > posL:#detecta se passou linha centro pra cima
                    detect.clear()
                    up += 1
                    total -= 1
                    cv2.line(frame, xy1, xy2, (0, 255, 0), 5)
                    continue

                if detect[c - 1][1] > posL and l[1] < posL:#detecta se passou linha centro pra baixo
                    detect.clear()
                    down += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, (0, 0, 255), 5)
                    continue

                if c > 0:
                    cv2.line(frame, detect[c - 1], l, (0, 0, 255), 1)

    cv2.putText(frame, "Total: " + str(total), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)#texto na tela
    cv2.putText(frame, "Saindo: " + str(up), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)#texto na tela
    cv2.putText(frame, "Entrando: " + str(down), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (196, 0, 0), 2)#texto na tela
    cv2.putText(frame, "Maximo: " + str(vmax), (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)#texto na tela
    if total>vmax:
        # Define the window's contents
        layout = [[sg.Text("contagem pessoas: ")], [sg.Input()],
                  [sg.Button('Ok')]]

        # Create the window
        window = sg.Window('Contagem Pessoas G4', layout)  # Part 3 - Window Defintion

        # Display and interact with the Window
        event, values = window.read()  # Part 4 - Event loop or Window.read call

        # Do something with the information gathered
        c = int(values[0])
        total=c

        # Finish up by removing from the screen
        window.close()  # Part 5 - Close the Window

    cv2.imshow("frame", frame)#janelinha do video

    if cv2.waitKey(30) & 0xFF == ord('q'): # pressiona o q para quebrar a linha e parar o programa
        break

cap.release()
cv2.destroyAllWindows()
