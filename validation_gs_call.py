from Validation import *
import time


def validation(ep_list, lr, arg, error_list):
    fail_count = 0

    for ep in ep_list:
        validation_fail_count = 0
        ep_statistics = statFetch(ep)
        actual_res, audio_rx, video_rx = stream_res_count(ep_statistics)

        # Validating RX stream count for GS..........
        print('#######Validating Video Rx received on GS##########\n')
        if video_rx == arg - 1:
            print(ep + " receiving " + str(video_rx) + " remote  streams ..Expected Stream Count  : " + str(
                arg - 1) + " Actual Stream count : " + str(video_rx) + " Result: [PASS]")
        else:
            print(ep + " receiving more or less number of streams " + str(video_rx) + " Actual Stream count : " + str(
                arg - 1) + " Result: [FAIL]")
            validation_fail_count += 1
            error_list.append("Receiving more or lesser number of streams than expected on GS {}".format(ep))
        print('#######Validation completed for video Rx on GS ##########\n\n')
        time.sleep(5)

        # Validating video resolution received  on  GS EP########

        print('#######Validating Resolutions for video RX  on GS##########\n')
        res_check_result = res_count_check(lr, arg, actual_res)
        if res_check_result == 0:
            print("Video Rx Resolution matched for all streams on GS: " + str(ep) + " Result: [PASS]")
        else:
            print("Video Rx Resolution mismatch issue observed on GS: " + str(ep) + " Result: [FAIL]")
            validation_fail_count += 1
            error_list.append("Video Rx Resolution mismatch issue observed on GS: {}".format(ep))
        print('#######Validation Completed for video RX  on GS##########\n\n')
        time.sleep(5)

        # Validating Bit Rate Used should not exceeds total negotiated bandwidth"

        print("#######Validating total bit rate used in call on GS " + ep + " ##########\n")
        BitRateUsed_result = max_bit_rate_calculation(ep_statistics, lr)
        if BitRateUsed_result == 0:
            print("Used Bandwidth lies with in negotiated bandwidth Result: [PASS]")
        else:
            print("Used Bandwidth exceeds negotiated bandwidth Result: [FAIL]")
            validation_fail_count += 1
            error_list.append("Used Bandwidth exceeds negotiated bandwidth on GS {}".format(ep))
        print("#######Validation completed for total bit rate used in call on GS" + ep + " ##########\n")
        time.sleep(5)

        # Validating Health of video Streams received on GS#######

        print("#######Validating quality of streams received on  GS " + ep + "##########\n")
        stream_quality_result = validate_streams_health(ep_statistics)
        if stream_quality_result == 0:
            print("GS :" + str(ep) + " receiving good quality streams in conference Result: [PASS]")
        else:
            print("GS :" + str(ep) + " receiving bad quality streams in conference Result: [FAIL]")
            validation_fail_count += 1
            error_list.append("GS {} receiving bad quality Video Rx stream ".format(ep))
        print("#######Validating completed for checking quality  received on GS " + ep + " ##########\n\n")

        if validation_fail_count != 0:
            fail_count += 1
        time.sleep(10)
    if fail_count == 0:
        return 0, error_list
    else:
        return 1, error_list
