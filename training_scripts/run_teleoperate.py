import subprocess
import sys

def run_teleoperate():
    """Run lerobot teleoperate with bimanual SO100 configuration."""
    cmd = [
        sys.executable, "-m", "lerobot.teleoperate",
        "--robot.type=bi_so100_follower",
        "--robot.left_arm_port=/dev/tty.usbmodem5A680122821",
        "--robot.right_arm_port=/dev/tty.usbmodem5A680121381",
        "--robot.id=bimanual_follower",
        "--teleop.type=bi_so100_leader",
        "--teleop.left_arm_port=/dev/tty.usbmodem5A680110941",
        "--teleop.right_arm_port=/dev/tty.usbmodem5A680135321",
        "--teleop.id=bimanual_leader",
        "--display_data=true"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("Process interrupted by user")
        return 130

if __name__ == "__main__":
    run_teleoperate()