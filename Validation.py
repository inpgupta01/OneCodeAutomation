import json
import urllib.request
import ssl

pre = 'https://'
post = '/rest/conferences/0/mediastats?'

expected_res_count = {
    3: {2048: {'actual_1080p_stream_count': 1, 'actual_720p_stream_count': 0, 'actual_360p_stream_count': 1,
               'actual_180p_stream_count': 0},
        1920: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 1, 'actual_360p_stream_count': 1,
               'actual_180p_stream_count': 0},
        1024: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 1, 'actual_360p_stream_count': 1,
               'actual_180p_stream_count': 0},
        768: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 1, 'actual_360p_stream_count': 1,
              'actual_180p_stream_count': 0},
        512: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 0,
              'actual_360p_stream_count': 2, 'actual_180p_stream_count': 0}},

    5: {2048: {'actual_1080p_stream_count': 1, 'actual_720p_stream_count': 0, 'actual_360p_stream_count': 4,
               'actual_180p_stream_count': 0},
        1920: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 1, 'actual_360p_stream_count': 4,
               'actual_180p_stream_count': 0},
        1024: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 1, 'actual_360p_stream_count': 1,
               'actual_180p_stream_count': 0},
        768: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 1, 'actual_360p_stream_count': 1,
              'actual_180p_stream_count': 0},
        512: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 5,
              'actual_360p_stream_count': 2, 'actual_180p_stream_count': 0.0}},

    7: {2048: {'actual_1080p_stream_count': 1, 'actual_720p_stream_count': 0, 'actual_360p_stream_count': 4,
               'actual_180p_stream_count': 0},
        1920: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 1, 'actual_360p_stream_count': 4,
               'actual_180p_stream_count': 0},
        1024: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 1, 'actual_360p_stream_count': 1,
               'actual_180p_stream_count': 0},
        768: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 1, 'actual_360p_stream_count': 1,
              'actual_180p_stream_count': 0},
        512: {'actual_1080p_stream_count': 0, 'actual_720p_stream_count': 5,
              'actual_360p_stream_count': 2, 'actual_180p_stream_count': 0}}}


def statFetch(ep_ip):
    url = pre + str(ep_ip) + post
    ssl._create_default_https_context = ssl._create_unverified_context
    data = urllib.request.urlopen(url).read()
    json_data = json.loads(data)
    print("Endpoint {} :".format(ep_ip))
    return json_data


def stream_res_count(json_data):
    video_Rx = 0
    audio_Rx = 0
    res_1080p_count = 0
    res_720p_count = 0
    res_360p_count = 0
    res_180p_count = 0

    for j in json_data:
        if j['mediaFormat'] == '1080p' and j['mediaStream'] == 'videoRx':
            video_Rx += 1
            res_1080p_count += 1
        elif (j['mediaFormat'] == '720p' or j['mediaFormat'] == '960x540') and j['mediaStream'] == 'videoRx':
            video_Rx += 1
            res_720p_count += 1
        elif (j['mediaFormat'] == '640x360' or j['mediaFormat'] == '640x368') and j['mediaStream'] == 'videoRx':
            video_Rx += 1
            res_360p_count += 1
        elif (j['mediaFormat'] == '320x192' or j['mediaFormat'] == '320x180') and j['mediaStream'] == 'videoRx':
            video_Rx += 1
            res_180p_count += 1
        elif j['mediaStream'] == 'audioRx':
            audio_Rx += 1

    stream_data = {'actual_1080p_stream_count': res_1080p_count, 'actual_720p_stream_count': res_720p_count,
                   'actual_360p_stream_count': res_360p_count, 'actual_180p_stream_count': res_180p_count}
    # print("Audio Rx : {}".format(audio_Rx))
    # print("Video Rx : {}".format(video_Rx))
    print(stream_data, "\n")

    return stream_data, audio_Rx, video_Rx


def res_count_check(lr, arg, actual_res_count):
    fail_res_count = 0
    for key in actual_res_count:
        if actual_res_count[key] == expected_res_count[arg][lr][key]:
            print("Stream count matched for " + str(key) + " resolution RESULT: PASS")
        else:
            print("Stream count matched for " + str(key) + " resolution RESULT: FAIL")
            fail_res_count += 1
    if fail_res_count == 0:
        return 0
    else:
        return 1


def max_bit_rate_calculation(json_data, lr):
    total_bit_rate_used = 0
    for i in json_data:
        if i['mediaStream'] == 'videoRx' or i['mediaStream'] == 'audioRx':
            total_bit_rate_used += i['actualBitRate']
    if total_bit_rate_used < lr:
        print("Total Bit Rate used by EP is " + str(total_bit_rate_used) + "kbps < Negotiated Bandwidth  " + str(
                lr) + "kbps")
        return 0
    else:
        print("Total Bit Rate used by EP is " + str(total_bit_rate_used) + "kbps exceeds Negotiated Bandwidth  " + str(lr) + "kbps")
        return 1


def validate_streams_health(json_data):
    negative = 0
    for i in json_data:
        if i['mediaStream'] == 'videoRx':
            print("\n \nValidating Health of " + i['mediaFormat'] + " stream")

            if i['actualBitRate'] <= i['bitRate'] + 30:
                print("Rx Bit Rate Used " + str(i['actualBitRate']) + " <= Max Bit Rate" +str(i['bitRate']) + " Upto +30 kbps is acceptable RESULT:[PASS]")
            else:
                print(
                    "Rx Bit Rate Used " + str(i['actualBitRate']) + " exceeds Max Receive Bit Rate" +
                    str(i['bitRate']) + " Upto +10 kbps is acceptable RESULT:[FAIL]")
                negative += 1
            if i['jitter'] < 20:
                print("Jitter value "+str(i['jitter'])+" which is less than 20 msec RESULT:[PASS]")
            else:
                print("Jitter value "+str(i['jitter'])+", which exceeds 20 msec RESULT:[FAIL]")
                negative += 1
            if i['percentPacketLoss'] <= 3.0:
                print("Packetloss percent is " + str(i['percentPacketLoss']) + " RESULT:[PASS]")
            else:
                print("Packetloss  percent is " + str(i['percentPacketLoss']) + " RESULT:[FAIL]")
                negative += 1
            if i['qualityIndicator'] == 100:
                print("Stream quality is good as quality indicator value is " + str(
                    i['qualityIndicator']) + " RESULT:[PASS]")
            else:
                print("Stream quality is not good  as quality indicator value is " + str(
                    i['qualityIndicator']) + " RESULT:[FAIL]")
                negative += 1
    if negative != 0:
        return 1
    else:
        return 0
