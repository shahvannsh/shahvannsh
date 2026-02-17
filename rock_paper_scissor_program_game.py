import random

options = ("rock", "paper", "scissors")
is_running = True

while is_running:
    
    player= None
    computer = random.choice(options)
    
    while player not in options:
        player = input("Enter a choice (rock,paper,scissors):")
    
        print(f"Player: {player}")
        print(f"Computer: {computer}")
        
        if player== computer:
            print("IT IS A TIE!")
        elif player == "rock" and computer == "scissors":
            print("You Win")
        elif player == "paper" and computer == "rock":
            print("You Win")
        elif player == "scissors" and computer == "paper":
            print("You Win")
            
        else:
            print("You Lose")

        if not input("Play again? (y/n)").lower() == "y": 
            is_running = False