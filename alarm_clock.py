#Python Alarm Clock
import time
import datetime
from playsound3 import playsound

def set_alarm(alarm_time):
    i = 0
    j = 0
    print(f"Alarm set for {alarm_time}")
    is_running = True
    

    while is_running:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(current_time)
        
        if current_time == alarm_time:
            print("Wake Up to Reality")

            while i < 3:
                playsound('C:/Users/itsva/Desktop/College/practice/Python_Learning/Alarm_clock/my_music.mp3', block=False)
                time.sleep(0.01)
                ques = input("Do You wanna stop the alarm or You want to snooze the alarm for 5 min ").upper()
                if ques == "STOP":
                    playsound('C:/Users/itsva/Desktop/College/practice/Python_Learning/Alarm_clock/my_music.mp3',block=False)
                    playsound('C:/Users/itsva/Desktop/College/practice/Python_Learning/Alarm_clock/my_music.mp3',block=False)
                    playsound('C:/Users/itsva/Desktop/College/practice/Python_Learning/Alarm_clock/my_music.mp3',block=False)
                    is_running = False
                    print("Alarm has been terminated")
                    break
                elif ques == "SNOOZE":
                    print("The alarm has been snoozed for 5 mins please wait ")
                    time.sleep(300)
                    continue
                else:
                    continue

        time.sleep(1)


if __name__ == '__main__':
    alarm_time = input("Enter the alarm time (HH:MM:SS): in 24hr format")
    set_alarm(alarm_time)