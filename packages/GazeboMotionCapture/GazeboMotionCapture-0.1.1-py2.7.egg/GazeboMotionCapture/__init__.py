from threading import Thread
import trollius
from trollius import From
import pygazebo
from pygazebo.msg import poses_stamped_pb2
from pyquaternion import Quaternion
from math import pi

loop = trollius.get_event_loop()

EXIT = False
def exit():
    EXIT = True
    loop.stop()
    print("exiting... motion captrue")

def parse_data(data):
    message = poses_stamped_pb2.PosesStamped.FromString(data)

    position = message.pose[0].position
    position = (position.y, position.x, position.z)

    orientation = message.pose[0].orientation

    q = Quaternion(orientation.w, orientation.x, orientation.y * -1.0, orientation.z * -1.0)
    convert_q = tuple(q*Quaternion(axis=[0, 0, 1], radians=pi * 0.5))

    callback(1, position, convert_q)

@trollius.coroutine
def subscribe_loop(address):
    manager = yield From(pygazebo.connect(address=address))

    manager.subscribe('/gazebo/default/pose/info',
                      'gazebo.msgs.PosesStamped',
                      parse_data)

    while not EXIT:
        yield From(trollius.sleep(0.2))

def loop_in_thread(loop, address):
    try:
        trollius.set_event_loop(loop)
        loop.run_until_complete(subscribe_loop(address))
    except Exception as e:
        print(e)

def create_motion_capture(address):
    motion_capture = Thread(target=loop_in_thread, args=(loop, address,))
    motion_capture.exit = exit
    return motion_capture

if __name__ == '__main__':
    def callback(id, position, orientation):
        print(id, position, orientation)
    motion_capture = create_motion_capture(('127.0.0.1', 11345), callback)
    motion_capture.start()

    import time
    time.sleep(5)
    motion_capture.exit()
