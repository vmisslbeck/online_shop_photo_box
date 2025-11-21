
# One time only

# only needed on Ubuntu
# sudo apt-get install python3-tk 

sudo apt install libgphoto2-6
sudo apt install gphoto2

python3 -m venv myvenv
source ./myvenv/bin/activate
pip install -r requirements.txt

sudo bash -c "curl https://cdn.odriverobotics.com/files/odrive-udev-rules.rules > /etc/udev/rules.d/91-odrive.rules && udevadm control --reload-rules && udevadm trigger"