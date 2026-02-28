#Timer 
import winsound
import time
def make_beep_sound(frequency, duration):
  try:
    winsound.Beep(frequency, duration)
  except RuntimeError:
    print("The system is not able to beep the speaker. Check if the terminal bell is muted.")
  except ImportError:
    print("winsound module is only available on Windows.")

print("Welcome to your personalized Timer\n ")
my_time = int(input("Enter the time in seconds: "))

for x in range(my_time,0,-1):
    seconds= x%60
    minute= int(x/60)%60
    hours= int(x/3600)
    print(f"{hours:02}:{minute:02}:{seconds:02}")
    time.sleep(1)
    
def repeat_beep(frequency, duration, repetitions, interval):
    for _ in range(repetitions):
        winsound.Beep(frequency, duration)
        time.sleep(interval)

repeat_beep(4300, 1000, 5 , 0.2)
print("TIMES UP")

print("Your Program has been terminated")