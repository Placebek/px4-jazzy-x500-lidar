import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
from pyzbar import pyzbar

class BoxBarcodeScanner(Node):
    def __init__(self):
        super().__init__('box_barcode_scanner')
        self.subscription = self.create_subscription(
            Image, '/camera', self.listener_callback, 10)
        self.br = CvBridge()
        self.model = YOLO('yolov8m.pt')
        self.total_barcodes = 0
        self.detected_barcodes = []  # Для уникальных штрих-кодов

    def listener_callback(self, data):
        frame = self.br.imgmsg_to_cv2(data, desired_encoding="bgr8")
        # Детекция только коробок (class 39 в COCO)
        results = self.model.predict(frame, classes=[39], conf=0.6, verbose=False)
        boxes = results[0].boxes.xyxy.cpu().numpy()

        for box in boxes:
            x1, y1, x2, y2 = map(int, box[:4])
            roi = frame[y1:y2, x1:x2]
            barcodes = pyzbar.decode(roi)
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                if barcode_data:
                    self.detected_barcodes.append(barcode_data)
                    self.total_barcodes += 1
                    self.get_logger().info(f"Штрих-код: {barcode_data}")
                # Отрисовка
                (bx, by, bw, bh) = barcode.rect
                cv2.rectangle(roi, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
                cv2.putText(roi, barcode_data, (bx, by - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        resized = cv2.resize(frame, (540, 317))
        cv2.imshow("Detected Frame", resized)
        cv2.waitKey(1)

    def destroy_node(self):
        self.get_logger().info(f"Работа завершена. Всего найдено штрих-кодов: {self.total_barcodes}")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = BoxBarcodeScanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()