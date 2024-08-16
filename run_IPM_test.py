"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Manually select points to get the projection map
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import argparse
import os
import numpy as np
import cv2
from surround_view import FisheyeCameraModel, PointSelector, display_image
import surround_view.param_settings as settings

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


def callback(image_msg):
    try:
        camera_name = args.camera
        camera_file = os.path.join(os.getcwd(), "yaml", camera_name + ".yaml")
        # 将 ROS 图像消息转换为 OpenCV 图像
        cv_image = bridge.imgmsg_to_cv2(image_msg, desired_encoding="bgr8")
        # image_file = os.path.join(os.getcwd(), "images", camera_name + ".png")
        # image = cv2.imread(image_file)
        camera = FisheyeCameraModel(camera_file, camera_name)
        camera.set_scale_and_shift(scale, shift)
        # und_image = camera.undistort(cv_image)
        proj_image = camera.project(cv_image)
    except CvBridgeError as e:
        rospy.logerr("CvBridge Error: {0}".format(e))
        return

    # 显示图像
    cv2.imshow("Origim Image", cv_image)
    # cv2.imshow("Undistort Image", und_image)
    cv2.imshow("Bird's View Image", proj_image)
    cv2.waitKey(30)  # 等待1毫秒，以便更新窗口


def main():
    global args
    global scale
    global shift
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-camera",
        required=True,
        choices=["front", "back", "left", "right"],
        help="The camera view to be projected",
    )
    parser.add_argument(
        "-scale", nargs="+", default=None, help="scale the undistorted image"
    )
    parser.add_argument(
        "-shift", nargs="+", default=None, help="shift the undistorted image"
    )
    args = parser.parse_args()

    if args.scale is not None:
        scale = [float(x) for x in args.scale]
    else:
        scale = (1.0, 1.0)
    print("scale:", scale)
    if args.shift is not None:
        shift = [float(x) for x in args.shift]
    else:
        shift = (0, 0)
    print("shift:", shift)
    rospy.init_node("image_listener", anonymous=True)

    global bridge
    bridge = CvBridge()

    # 订阅图像话题
    rospy.Subscriber("/camera/color/image_raw", Image, callback)

    # 保持节点运行
    rospy.spin()

    # 在节点关闭时关闭 OpenCV 窗口
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
