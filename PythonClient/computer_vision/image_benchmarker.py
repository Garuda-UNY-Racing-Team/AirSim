#!/usr/bin/env python
from argparse import ArgumentParser
from msgpackrpc.error import RPCError
import airsim
import time
import threading
import numpy as np
import cv2


class ImageBenchmarker():
    def __init__(self, 
            img_benchmark_type = 'simGetImage', 
            viz_image_cv2 = False):
        self.airsim_client = airsim.VehicleClient()
        self.airsim_client.confirmConnection()
        self.image_benchmark_num_images = 0
        self.image_benchmark_total_time = 0.0
        self.image_callback_thread = None
        self.viz_image_cv2 = viz_image_cv2
        if img_benchmark_type == "simGetImage":
            self.image_callback_thread = threading.Thread(target=self.repeat_timer_img, args=(self.image_callback_benchmark_simGetImage, 0.05))
        if img_benchmark_type == "simGetImages":
            self.image_callback_thread = threading.Thread(target=self.repeat_timer_img, args=(self.image_callback_benchmark_simGetImages, 0.05))
        self.is_image_thread_active = False

    def start_img_benchmark_thread(self):
        if not self.is_image_thread_active:
            self.is_image_thread_active = True
            self.image_callback_thread.start()
            print("Started img image_callback thread")

    def stop_img_benchmark_thread(self):
        if self.is_image_thread_active:
            self.is_image_thread_active = False
            self.image_callback_thread.join()
            print("Stopped image callback thread.")

    def repeat_timer_img(self, task, period):
        while self.is_image_thread_active:
            task()
            time.sleep(period)

    def print_benchmark_results(self):
        avg_fps = 1.0 / ((self.image_benchmark_total_time) / float(self.image_benchmark_num_images))
        print("result: {} avg_fps for {} num of images".format(avg_fps, self.image_benchmark_num_images))

    def image_callback_benchmark_simGetImage(self):
        self.image_benchmark_num_images += 1
        iter_start_time = time.time()
        image = self.airsim_client.simGetImage("fpv_cam", airsim.ImageType.Scene)
        np_arr = np.frombuffer(image, dtype=np.uint8)
        img_rgb = np_arr.reshape(240, 512, 4)
        self.image_benchmark_total_time += time.time() - iter_start_time
        avg_fps = 1.0 / ((self.image_benchmark_total_time) / float(self.image_benchmark_num_images))
        print("result: {} avg_fps for {} num of images".format(avg_fps, self.image_benchmark_num_images))
        # uncomment following lines to viz image
        if self.viz_image_cv2:
            cv2.imshow("img_rgb", img_rgb)
            cv2.waitKey(1)

    def image_callback_benchmark_simGetImages(self):
        self.image_benchmark_num_images += 1
        iter_start_time = time.time()
        request = [airsim.ImageRequest("fpv_cam", airsim.ImageType.Scene, False, False)]
        try:
            response = self.airsim_client.simGetImages(request)
            np_arr = np.frombuffer(response[0].image_data_uint8, dtype=np.uint8)
            img_rgb = np_arr.reshape(response[0].height, response[0].width, 4)
            self.image_benchmark_total_time += time.time() - iter_start_time
            avg_fps = 1.0 / ((self.image_benchmark_total_time) / float(self.image_benchmark_num_images))
            print("result + {} avg_fps for {} num of images".format(avg_fps, self.image_benchmark_num_images))
            # uncomment following lines to viz image
            if self.viz_image_cv2:
                cv2.imshow("img_rgb", img_rgb)
                cv2.waitKey(1)
        except RPCError as e:
            print("%s" % str(e))
            print("Are your camera name & vehicle name correct?")

def main(args):
    baseline_racer = ImageBenchmarker(img_benchmark_type=args.img_benchmark_type, viz_image_cv2=args.viz_image_cv2)
 
    baseline_racer.start_img_benchmark_thread()
    time.sleep(30)
    baseline_racer.stop_img_benchmark_thread()
    baseline_racer.print_benchmark_results()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--img_benchmark_type', type=str, choices=["simGetImage", "simGetImages"], default="simGetImages")
    parser.add_argument('--enable_viz_image_cv2', dest='viz_image_cv2', action='store_true', default=False)

    args = parser.parse_args()
    main(args)

