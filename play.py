import numpy as np
import time
import os
import cv2
import argparse
from skimage.measure import compare_ssim
from sklearn.cluster import KMeans

def find_diff(fig1,fig2, num):
    grayA = cv2.cvtColor(fig1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(fig2, cv2.COLOR_BGR2GRAY)
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")
    pots = np.where(diff<250)
    points = [[pots[1][i], pots[0][i]]for i in range(len(pots[0]))]
    km = KMeans(num).fit(points)
    ps = km.cluster_centers_
    return ps
	
def run(num, interval=0):
    next_fig = np.load('next_fig.npy')
    new_fig = 1
    while 1:
        print('Ready!')
        if new_fig:
            os.system('adb shell screencap -p /sdcard/1.png')
            os.system('adb pull /sdcard/1.png state.png')
            state = cv2.imread('state.png')

        picup = state[110:660,141:692,:]
        picdown = state[684:1234,141:692,:]
        state_fig = state[1246:1274,291:428,:]

        ps = find_diff(picup, picdown, num)

        loc = [[142+int(i[0]), 111+int(i[1])] for i in ps]

        for i in loc:
            cmd = 'adb shell input tap {} {}'.format(i[0],i[1])
            print(cmd)
            os.system(cmd)
            time.sleep(interval)

        print('finish!')
        time.sleep(2)
    
        os.system('adb shell screencap -p /sdcard/1.png')
        os.system('adb pull /sdcard/1.png state.png')
        state = cv2.imread('state.png')

        if (state[1130:1216,420:662] == next_fig).all():
            cmd = 'adb shell input tap {} {}'.format(541,1173)
            print(cmd)
            os.system(cmd)
            time.sleep(7)
            new_fig = 1
        elif (state[1246:1274,291:428,:] == state_fig).all():
            input('有未找对位置，请手动找出后回车继续')
            new_fig = 1
        else:
            new_fig = 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num', default='3', type=int, help='number of different places')
    parser.add_argument('--interval', default='0', type=int, help='the preiod between two clicks')
    args = parser.parse_args()
    run(args.num, args.interval)