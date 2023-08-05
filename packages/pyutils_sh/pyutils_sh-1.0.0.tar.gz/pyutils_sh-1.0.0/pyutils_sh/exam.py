import csv
import os
import pandas as pd


def grade_scantron(input_scantron, correct_answers, drops=[], 
                   item_value=1, incorrect_threshold=0.5):
    """
     - Compiles scantron data and calculates exam grades for each student.
     - Also provides a summary of exam performance, as well as a list of the questions "most" students got incorrect and saves the distribution of answers for those poorly performing questions
     - Takes 1 scantron text file and outputs 2 summary grade files.
     - Splitting of the scantron file is specific to each scantron machine. The indices used in this script are correct for the scantron machine in the UBC Psychology department. Indices need to be adjusted for different machines.
     - Scantron exams can be finicky. Students who incorrectly fill out scantrons need to be considered. Make sure to manually inspect the text file output by the scantron machine for missing answers etc. before running this. This script does not correct for human error when filling out the scantron.
    
    # text file generated from scantron machine (make sure to manually inspect
    # the scantron file first to make sure there are no missing answers etc.)
    inputFile = input_scantron
    
    # list of question numbers to be dropped from all calculations e.g. [1, 3, 5]
    dropItems = drops
    
    # how many points is each MC question worth?
    itemWorth = item_value
    
    # Threshold for the summary file. Questions where the correct count is
    # less than this proportion/threshold are flagged in the output summary
    # file
    incorrectThreshold = incorrect_threshold
    
    # list containing the CORRECT answers for each question. Update this for
    # every exam
    #    correctAnswers = [
    #        "A",  # 1
    #        "B",  # 2
    #        "D",  # 3
    #        "B",  # 4
    #        "C",  # 5
    #        "D",  # 6
    #        "C",  # 7
    #        "E",  # 8
    #        "A",  # 9
    #        "E"  # 10
    #    ]
    """
    
    # Start and end locations of various pieces of information in the scantron text file.
    # These need to be adjusted for different scantron machine.
    # Currently set for the machine used in UBC Psychology
    surname_idx = (0, 12)
    first_name_idx = (12, 21)
    student_num_idx = (21, 30)
    answers_idx = 30
    
    # output directory
    directory, filename = os.path.split(input_scantron)
    filename = os.path.splitext(filename)[0]
    
    # calculate total number of points available on the exam
    total_points = (len(correct_answers)*item_value) - len(drops)
    
    # create a pandas dataframe to hold the scantron data
    summary = ["surname", "first_name", "student_number", "points", "percent"]
    questions = ["Q-{}".format(i+1) for i in range(len(correct_answers))]
    
    df = pd.DataFrame(columns=summary+questions)
    
    # calculate grades
    with open(input_scantron, 'r') as f:
        scantron_data = csv.reader(f)
    
        # loop through every row (student) in the input scantron file
        for row in scantron_data:
            surname = row[0][surname_idx[0]:surname_idx[1]].lstrip().rstrip()
            first_name = row[0][first_name_idx[0]:first_name_idx[1]].lstrip().rstrip()
            student_num = row[0][student_num_idx[0]:student_num_idx[1]].lstrip().rstrip()
            answers = row[0][answers_idx:(answers_idx+len(correct_answers))]
            
            points = 0
            
            for i, pair in enumerate(zip(answers, correct_answers)):
                if i+1 not in drops:
                    if pair[0] == pair[1]:
                        points += item_value
            
            df_summary = {"surname": surname,
                          "first_name": first_name,
                          "student_number": student_num,
                          "points": points,
                          "percent": (points/total_points)*100}
            
            df_questions = {"Q-{}".format(i+1): a for i, a in enumerate(answers)}
            
            df = df.append([{**df_summary, **df_questions}], ignore_index=True)
        
    df.to_excel(os.path.join(directory, "{}.xls".format(filename + "_grades")),
                sheet_name="grades", index=False)
    
    # write summary statistics
    with open(os.path.join(directory, "{}.txt".format(filename + "_summary")), 'w') as f:
        # calculate descriptive statistics   
        N = df.shape[0]
        mean_percent = df["percent"].mean()
        mean_points = df["points"].mean()
        std_points = df["points"].std()
        range_points = (df["points"].min(), df["points"].max())
        
        f.writelines([
            "Descriptive Statistics: \n\n",
            "N: {}\n".format(N),
            "Mean %: {:.2f}%\n".format(mean_percent),
            "Mean score (out of {} points): {:.2f}\n".format(total_points,
                                                             mean_points),
            "Score SD: {:.2f}\n".format(std_points),
            "Range: {} (Min: {}, Max: {})\n\n\n".format(range_points[1]-range_points[0],
                                                  range_points[0], range_points[1])
        ])
            
        if len(drops) > 0:
            f.writelines(["Dropped questions: {}\n\n\n".format(", ".join(map(str, drops)))])
        
        f.writelines([
            "Problem Items (questions that less " \
            "than {}% of students got correct):\n\n".format(incorrect_threshold*100)
        ])
            
        problems = False
        
        for i, item in enumerate(questions):
            cur_q = df[item]
            
            if len(cur_q[cur_q == correct_answers[i]]) < (N * incorrect_threshold):
                problems = True
                distribution = cur_q.value_counts()
                
                f.writelines([
                        "{} (A: {}, B: {}, C: {}, D: {}, E: {})\n".format(
                            cur_q.name, distribution.A, distribution.B,
                            distribution.C, distribution.D, distribution.E)
                        ])
                        
        if not problems:
            f.writelines(["None"])
