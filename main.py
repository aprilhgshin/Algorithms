import os
from TSP import algorithm


if __name__ == "__main__":
    for file in os.listdir(os.getcwd() + '/inputs'):
        print(file)
        try:
            algorithm(os.getcwd() + '/inputs/' + file, os.getcwd() + '/outputs/' + file.replace('.in', '.out'))
        except Exception as e:
            with open('errors', 'a') as error_file:
                error_file.write("Error while processing file: {}\n".format(file))
                error_file.write("{}\n".format(e))


