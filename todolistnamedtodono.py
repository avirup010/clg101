##this is a todo list app named todono that helps you to make basic todo lists.



tasks = []
def addtask():
    task = input("Please enter a task :)")
    tasks.append(task)
    print(f"Task '{task}' has been added to the list.")
def listtasks():
    if not tasks:
        print("There are no tasks currently.")
    else:
        print("Current tasks : ")
        for index, task in enumerate(tasks):
            print(f"Task #'{index}' '{task}'")
def deletetask():
    listtasks()
    try:
        tasktoDelete = int(input("Enter the task# to delete: "))
        if tasktoDelete >= 0 and tasktoDelete < len(tasks):
            tasks.pop(tasktoDelete)
            print(f"Task #'{tasktoDelete}' has been removed.")
        else :
            print(f"Task #'{tasktoDelete}' was not found.")
    except:
            print("Invalid Input")

if __name__ == "__main__" :
    print("Welcome to todono")
    while True:
        print("\n")
        print("Please select one of the following options")
        print("__________________________________________")
        print("1. Add a new task ")
        print("2. Delete a task ")
        print("3. List tasks ")
        print("1. Quit ")
        choice = input("Enter your choice: ")
        if(choice == "1"):
            addtask()
        elif(choice == "2"):
            deletetask()
        elif(choice == "3"):
            listtasks()
        elif(choice == "4"):
            break
        else:
            printf("Invalid Input. Please try again.")
    print("You are now exiting the app. Goodbye.")