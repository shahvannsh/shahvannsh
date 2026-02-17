#Python game

questions=("Which keyword is used to define a function in Python?",
          "What data type is the object L = [1, 23, 'hello', 1]?",
          "What is the main ingredient in traditional Japanese miso soup?",
          "What year did the Titanic sink?",
          "Which method is used to add an item to the end of a list?")

option=(("A.def","B.len","C. length","D.sort"),
        ("A.Dicitionary","B.tuple","C. set","D.list"),
        ("A.tofu","B.miso paste","C. seaweed","D.fish"),
        ("A.1910","B.1920","C. 1912","1915"),
        ("A. append","B.reverse","C. push","D.addto"))


answers=("A","D","B","C","A")
guesses=[]
score=0
question_num = 0

for question in questions:
    print("----------------------------------------------------------------------")
    print(question)

    for options in option[question_num]:
        print(options)

    guess = input("Enter (A,B,C,D): ").upper()
    guesses.append(guess)
    if guess == answers[question_num]:
        score += 1
        print("Correct choice: ")
    else:
        print("Incorrect choice")
        print(f"{answers[question_num]} is the correct answer")
    question_num += 1

print("-------------------------------------------------------------------------")
print("                              RESULT                                     ")
print("-------------------------------------------------------------------------")

print("answer:",end="")
for answer in answers:
    print(answer, end=" ")
print()

print("guesses: ", end=" ")
for guess in guesses:
    print(guess, end=" ")
print()

score = int(score / len(questions) * 100)
print(f"Your score is: {score}%")
