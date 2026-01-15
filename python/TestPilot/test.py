# A simple program to calculate average score of students

def calculate_average(scores):
    total = 0
    for i in range(len(scores)):
        total = total + scores[i]
    return total / len(scores)


def main():
    scores = input("Enter student scores separated by commas: ")
    scores_list = scores.split(",")

    avg = calculate_average(scores_list)

    if avg > 90:
        print("Excellent performance")
    elif avg > 75:
        print("Good performance")
    elif avg > 50:
        print("Average performance")
    else:
        print("Poor performance")

    print("Average score is: " + avg)


main()
