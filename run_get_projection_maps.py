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
        success = get_projection_map(camera, cv_image)
        if success:
            print("saving projection matrix to yaml")
            camera.save_data()
        else:
            print("failed to compute the projection map")
    except CvBridgeError as e:
        rospy.logerr("CvBridge Error: {0}".format(e))
        return

    # 显示图像
    cv2.imshow("Camera Image", cv_image)
    cv2.waitKey(30)  # 等待1毫秒，以便更新窗口


def get_projection_map(camera_model, image):

    name = camera_model.camera_name
    gui = PointSelector(image, title=name)
    dst_points = settings.project_keypoints[name]
    choice = gui.loop()
    if choice > 0:
        src = np.float32(gui.keypoints)
        dst = np.float32(dst_points)
        camera_model.project_matrix = cv2.getPerspectiveTransform(src, dst)
        # und_image = camera_model.undistort(image)
        proj_image = camera_model.project(image)

        ret = display_image("Bird's View", proj_image)
        if ret > 0:
            return True
        if ret < 0:
            cv2.destroyAllWindows()

    return False


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
