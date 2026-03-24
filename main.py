#===============================================================================
# Exemplo: segmentação de uma imagem em escala de cinza.
#-------------------------------------------------------------------------------
# Autor: Bogdan T. Nassu
# Universidade Tecnológica Federal do Paraná
#===============================================================================

import sys
import timeit
import numpy as np
import cv2

#===============================================================================

INPUT_IMAGE =  '/arroz.bmp'

# TODO: ajuste estes parâmetros!
NEGATIVO = False
THRESHOLD = 0.78
ALTURA_MIN = 1
LARGURA_MIN = 1
N_PIXELS_MIN = 20

#===============================================================================

def binariza (img, threshold):
    ''' Binarização simples por limiarização.

Parâmetros: img: imagem de entrada. Se tiver mais que 1 canal, binariza cada
              canal independentemente.
            threshold: limiar.
            
Valor de retorno: versão binarizada da img_in.'''

    img_out = np.where(img>threshold,-1.0,0.0)
    return img_out

#-------------------------------------------------------------------------------

def rotula (img, largura_min, altura_min, n_pixels_min):
    '''Rotulagem usando flood fill. Marca os objetos da imagem com os valores
[0.1,0.2,etc].

Parâmetros: img: imagem de entrada E saída.
            largura_min: descarta componentes com largura menor que esta.
            altura_min: descarta componentes com altura menor que esta.
            n_pixels_min: descarta componentes com menos pixels que isso.

Valor de retorno: uma lista, onde cada item é um vetor associativo (dictionary)
com os seguintes campos:

'label': rótulo do componente.
'n_pixels': número de pixels do componente.
'T', 'L', 'B', 'R': coordenadas do retângulo envolvente de um componente conexo,
respectivamente: topo, esquerda, baixo e direita.'''

    lista_arrozes = []

    rows, cols = img.shape[:2]
    rotulo = 0.1
    for row in range (rows):
        for col in range (cols):
            if img[row,col,0] == -1:
                n_pixels, T, L, B, R = flood_fill(img, row, col, rotulo, rows, cols, -1, -1)
                arroz = {"label": rotulo, "n_pixels": n_pixels,"T": T, "L": L, "B": B, "R": R }
                if B - T + 1 >= altura_min and R - L + 1 >= largura_min and n_pixels >= n_pixels_min:
                    lista_arrozes.append(arroz)
                rotulo += 0.1
    return lista_arrozes

#-------------------------------------------------------------------------------
def flood_fill(img, row, col, rotulo, T, L, B, R):
    # Verifica se ainda ta na imagem e se ja foi rotulado
    if row >= img.shape[0] or col >= img.shape[1] or row < 0 or col < 0 or img[row, col, 0] != -1:
        return (0, img.shape[0], img.shape[1], -1, -1)
   
    img[row,col, 0] = rotulo

    # Menor row é mais acima
    T = min(T, row)
    # Menor col é mais a esquerda
    L = min(L, col)
    # Maior row é mais abaixo
    B = max(B, row)
    # Maior col é mais a direita
    R = max(R, col)

    dir = (0, img.shape[0], img.shape[1], -1, -1)
    esq = (0, img.shape[0], img.shape[1], -1, -1)
    cima = (0, img.shape[0], img.shape[1], -1, -1)
    baixo = (0, img.shape[0], img.shape[1], -1, -1)

    # Recursão
    dir = flood_fill(img, row, col + 1, rotulo, T, L, B, R)
    esq = flood_fill(img, row, col - 1, rotulo, T, L, B, R)
    cima = flood_fill(img, row - 1, col, rotulo, T, L, B, R)
    baixo = flood_fill(img, row + 1, col, rotulo, T, L, B, R)
  
    n_pixels = dir[0] + esq[0] + cima[0] + baixo[0] + 1
    T = min(T, dir[1], esq[1], cima[1], baixo[1])
    L = min(L, dir[2], esq[2], cima[2], baixo[2])
    B = max(B, dir[3], esq[3], cima[3], baixo[3])
    R = max(R, dir[4], esq[4], cima[4], baixo[4])
    
    return n_pixels, T, L, B, R

#===============================================================================

def main ():

    # Abre a imagem em escala de cinza.
    img = cv2.imread (INPUT_IMAGE, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print ('Erro abrindo a imagem.\n')
        sys.exit ()

    # É uma boa prática manter o shape com 3 valores, independente da imagem ser
    # colorida ou não. Também já convertemos para float32.
    img = img.reshape ((img.shape [0], img.shape [1], 1))
    img = img.astype (np.float32) / 255

    # Mantém uma cópia colorida para desenhar a saída.
    img_out = cv2.cvtColor (img, cv2.COLOR_GRAY2BGR)

    # Segmenta a imagem.
    if NEGATIVO:
        img = 1 - img
    img = binariza (img, THRESHOLD)
    cv2.imshow ('01 - binarizada', img)
    cv2.imwrite ('01 - binarizada.png', img*255)

    start_time = timeit.default_timer ()
    componentes = rotula (img, LARGURA_MIN, ALTURA_MIN, N_PIXELS_MIN)
    n_componentes = len (componentes)
    print ('Tempo: %f' % (timeit.default_timer () - start_time))
    print ('%d componentes detectados.' % n_componentes)

    # Mostra os objetos encontrados.
    for c in componentes:
        cv2.rectangle (img_out, (c ['L'], c ['T']), (c ['R'], c ['B']), (0,0,1))

    cv2.imshow ('02 - out', img_out)
    cv2.imwrite ('02 - out.png', img_out*255)
    cv2.waitKey ()
    cv2.destroyAllWindows ()


if __name__ == '__main__':
    main ()

#===============================================================================
