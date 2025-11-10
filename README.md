
---

# 🛰 Autonomous Inventory Drone (LiDAR Simulation)

**Описание проекта**
Данный проект демонстрирует интеграцию **2D LiDAR-сенсора** с дроном **Holybro X500** в симуляции **Gazebo Harmonic** с использованием **ROS 2 Jazzy** и **PX4 Autopilot v1.15.0**.
Цель текущего этапа — **настройка подключения LiDAR и визуализация данных сканирования** через `rviz2`.
Функции распознавания объектов и штрих-кодов будут добавлены на следующих этапах разработки.

---

## 🙏 Благодарность

Благодарность пользователю [**monemati**](https://github.com/monemati) за репозиторий [RTABMap-ROS2-PX4](https://github.com/monemati/RTABMap-ROS2-PX4), послуживший основой для интеграции ROS 2, PX4 и Gazebo.

---

## 🎥 Демо проекта
[![Смотреть демо](https://img.youtube.com/vi/hLpDUYaxzWk/hqdefault.jpg)](https://youtu.be/hLpDUYaxzWk)


## ⚙️ Среда тестирования

* **ОС**: Ubuntu 24.04 LTS (Noble)
* **ROS 2**: Jazzy Jalisco
* **Gazebo**: Harmonic
* **PX4-Autopilot**: v1.15.0

---

## 🔧 Установка

### 1. Создать виртуальное окружение

```bash
python3 -m venv ~/px4-venv
source ~/px4-venv/bin/activate
```

### 2. Клонировать проект

```bash
git clone https://github.com/Placebek/px4-jazzy-x500-lidar.git
cd px4-jazzy-x500-lidar
```

### 3. Установить PX4-Autopilot (v1.15.0)

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive -b v1.15.0
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh
make px4_sitl
```

### 4. Установить ROS 2 Jazzy

```bash
sudo apt update && sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

sudo apt install software-properties-common curl -y
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update && sudo apt upgrade -y
sudo apt install ros-jazzy-desktop ros-jazzy-ros-gz-bridge ros-dev-tools ros-jazzy-rtabmap-ros -y
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 5. Установить Micro XRCE-DDS Agent

```bash
cd ~
git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
mkdir build && cd build
cmake ..
make
sudo make install
sudo ldconfig /usr/local/lib/
```

---

## ⚙️ Конфигурация PX4 и моделей

Добавьте в `~/.bashrc`:

```bash
source /opt/ros/jazzy/setup.bash
export GZ_SIM_RESOURCE_PATH=/opt/ros/jazzy/share:~/PX4-Autopilot/Tools/simulation/gz/models:~/px4-jazzy-x500-lidar/models
export GZ_SIM_WORLD_PATH=~/PX4-Autopilot/Tools/simulation/gz/worlds
```

Затем:

```bash
source ~/.bashrc
```

Скопируйте модели и миры:

```bash
cp -f ~/px4-jazzy-x500-lidar/models/* ~/PX4-Autopilot/Tools/simulation/gz/models
cp -f ~/px4-jazzy-x500-lidar/worlds/* ~/PX4-Autopilot/Tools/simulation/gz/worlds
cp -f ~/px4-jazzy-x500-lidar/airframes/* ~/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes
```

Пересоберите PX4:

```bash
cd ~/PX4-Autopilot
make px4_sitl
```

---

## 🚀 Запуск симуляции LiDAR

### Терминал 1 — Micro XRCE Agent

```bash
cd ~/Micro-XRCE-DDS-Agent/build
./MicroXRCEAgent udp4 -p 8888
```

### Терминал 2 — PX4 + Gazebo

```bash
cd ~/PX4-Autopilot
PX4_SYS_AUTOSTART=4012 PX4_GZ_WORLD=warehouse PX4_GZ_MODEL=x500_lidar make px4_sitl gz_x500_lidar
```

### Терминал 3 — ROS-мост для LiDAR

```bash
ros2 run ros_gz_bridge parameter_bridge /world/warehouse/model/x500_lidar_0/link/link/sensor/lidar_2d_v2/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan /camera@sensor_msgs/msg/Image@gz.msgs.Image
```

# Терминал 4 — Запуск окно управление дроном 
```bash
cd ~/px4-jazzy-gazebo-yolov8
python keyboard-mavsdk-test.py
```
 - Нажмите `r` для взлёта, `WASD` для движения, `l` для посадки в `avoidance_mavsdk.py` (если интегрировано).


### Проверка топиков

```bash
ros2 topic list
```

Должен появиться топик:

```
/world/warehouse/model/x500_lidar_0/link/link/sensor/lidar_2d_v2/scan
```

---

## 👁️ Визуализация данных LiDAR в RViz2

```bash
rviz2
```

1. В левом верхнем углу установите **Fixed Frame** = тот, что указан в `ros2 topic echo` (обычно `link`).
2. Нажмите **Add → By topic → LaserScan** и выберите топик `/world/warehouse/model/x500_lidar_0/link/link/sensor/lidar_2d_v2/scan`.
3. Настройте параметры:

   * **Decay Time**: `0.1`
   * **Size (Meters)**: `0.01`
   * **Alpha**: `0.5`

Если ничего не отображается — убедитесь, что сенсор включён и топик публикуется.

---

## 📚 Источники

* [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot)
* [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/)
* [Gazebo Harmonic](https://gazebosim.org/)
* [RTAB-Map ROS 2](https://github.com/introlab/rtabmap_ros)
* [RTABMap-ROS2-PX4 (monemati)](https://github.com/monemati/RTABMap-ROS2-PX4)

---