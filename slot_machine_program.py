#Slot machine game

import random

def spin():
    symbol = ['🍒','🍉','🍋','🔔','⭐']
    
    return [random.choice(symbol) for _ in range(3)]

def print_r(row):
    print("*******************")
    print(" | ".join(row))
    print("*******************")

def get_pay(row , bet ):
    if row[0] == row[1] == row[2]:
        if row[0] == '🍒':
            return bet*3
        elif row[0] == '🍉':
            return bet*4
        elif row[0] == '🍋':
            return bet*5
        elif row[0] == '🔔':
            return bet*10
        elif row[0] == '⭐':
            return bet*20
    return 0

def main():
    balance = 100
    
    print("***********************")
    print("Welcome to Slot machine")
    print("🍒,🍉,🍋,🔔,⭐")
    print("***********************")
    
    while balance >0:
        print(f"Current balance is {balance} INR ")
        
        bet = input("Enter the bet amount (in INR) ")
        
        if not bet.isdigit(): 
            print("Please enter a vaild bet")
            continue
        
        bet = int(bet)
        
        if bet > balance:
            print("Insufficent Funds")
            continue
        
        if bet <= 0:
            print("Bet must be greater than 0")
            continue
        balance -= bet
        
        row = spin()
        print("Spinning....")
        print_r(row)
        
        
        payout = get_pay(row, bet)
        
        if payout >0:
            print(f" you won INR {payout}")
        else:
            print("*************************")
            print("Sorry you lost this round")
            print("*************************")
            
        balance += payout
        
        play_again = input("Do you want to spin again? (Y/N): ").lower()
        
        if play_again!= 'y':
            break
    
    print("**********************************************")
    print(f"Game over! Your Final balance is INR{balance}")
    print("**********************************************")
   

     
if __name__ =='__main__':
    main()