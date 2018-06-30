#!/usr/bin/python

vk_service_key = '7e03e4387e03e4387e03e438ba7e60d4b677e037e03e438251569b75882cada3c7f13ec'
api_key = 'f8afe185f4e9428b95952eddd8ae8738'
api_base_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0'

user_id = 94451685
ver = '5.78'
cnt = 100
src = 'src_xxxbig'
sleep_time = 2

import vk
session = vk.Session(vk_service_key)
api = vk.API(session)

import cognitive_face as FaceAPI
FaceAPI.Key.set(api_key)
FaceAPI.BaseUrl.set(api_base_url)

def retrieve_photo(to_file = './data_vk/vkdata.csv'):
    result = 0
    file_out = None
    try:
        file_out = open(to_file, 'w')
        friends = api.friends.get(user_id = user_id, version = ver, fields = 'deactivated')
        for friend in friends:
            if 'deactivated' in friend.keys():
                continue
            photos = api.photos.get(owner_id = friend['user_id'],
                version = ver,
                album_id = 'profile',
                extended = 1,
                count = cnt)
            for photo in photos:
                if src in photo.keys():
                    file_out.write('\"{}\",{}\n'.format(photo[src], photo['likes']['count']))
                    result += 1
    except Exception as some_exception:
        print(str(some_exception))
        result = -1
    finally:
        if hasattr(file_out, 'close'):
            file_out.close()
    return result

import csv
import time

def emotion_recognition(from_file = './data_vk/vkdata.csv', begin = 0, to_file = './data/data.csv'):
    csv_file = open(from_file, 'r')
    reader = csv.reader(csv_file)
    rows = [(row[0], int(row[1])) for row in reader]
    rows = rows[begin : ]
    csv_file.close()

    count = begin
    try:
        file_out = open(to_file, 'a')
        if begin == 0:
            file_out.write('happiness,amplitude,likes_count\n')
        for row in rows:
            avg_max = happiness_and_amplitude(row[0])
            if avg_max is not None:
                new_row = '{},{},{}\n'.format(avg_max[0], avg_max[1], row[1])
                file_out.write(new_row)
                print(row[0])
                print(new_row)
            count += 1
            time.sleep(sleep_time)
    except Exception as some_exception:
        print(str(some_exception))
    finally:
        if hasattr(file_out, 'close'):
            file_out.close()
        print(count)

def happiness_and_amplitude(src):
    faces = face_detect(src)
    if len(faces) > 0:
        happiness = avg_happiness(faces)
        amplitude = max_amplitude(faces)
        return happiness, amplitude
    else:
        return None

def face_detect(src):
    return FaceAPI.face.detect(src,
        False,
        False,
        'smile,emotion')

def avg_happiness(faces):
    happiness = 0
    for face in faces:
        happiness += face['faceAttributes']['smile']
    return happiness / len(faces)

def max_amplitude(faces):
    max_amplitude = -1
    for face in faces:
        emotions = face['faceAttributes']['emotion']
        emotions.pop('neutral', -1)
        amplitude = max(emotions.values()) - min(emotions.values())
        if amplitude > max_amplitude:
            max_amplitude = amplitude
    return max_amplitude

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import patsy as pt

def evaluate_dependence(from_file = './data/data.csv'):
    """
    data.csv : happiness, amplitude, likes_count
    """
    data_frame = pd.read_csv(from_file)
    data_frame.iloc[:, -1] = data_frame.iloc[:, -1] / max(data_frame.iloc[:, -1])

    x = data_frame.iloc[:, 0:2]
    z = data_frame.iloc[:, 2]

    linspace = np.linspace(0, 1, 1000)
    r_exp = ["likes_count ~ happiness", "likes_count ~ amplitude"]

    for i in range(2):
        dm_y, dm_x = pt.dmatrices(r_exp[i], data_frame)
        coef = np.linalg.lstsq(dm_x, dm_y)[0].ravel()
        print(coef)
        plt.subplot(2, 1, i + 1)
        plt.plot(x.iloc[:, i], z, 'go', color = 'blue')
        f_val = coef[0] + coef[1] * linspace
        plt.plot(linspace, f_val, color = 'red')
    plt.show()

def main(argv_first):
    if argv_first < 0:
        evaluate_dependence()
    elif argv_first == 0:
        retrieve_photo()
        emotion_recognition()
        evaluate_dependence()
    else:
        emotion_recognition(begin = argv_first)
        evaluate_dependence()

def isint(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

import sys

if __name__ == "__main__":
    argv_first = 0
    if len(sys.argv) > 1 and isint(sys.argv[1]):
        argv_first = int(sys.argv[1])
    main(argv_first)
