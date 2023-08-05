"""
Functions for aggregating and analyzing exam-related data, such as calculating 
student exam performance.
"""

import csv
import os
import pandas as pd


def grade_scantron(input_scantron, correct_answers, drops=[], 
                   item_value=1, incorrect_threshold=0.5):
    """
    Calculate student grades from scantron data.

    Compiles data collected from a scantron machine (5-option multiple choice 
    exam) and calculates grades for each student. Also provides descriptive 
    statistics of exam performance, as well as a list of the questions "most" 
    students got incorrect, and saves the distribution of answers for those 
    poorly performing questions.
    
    This function receives 1 scantron text file and produces 2 output files. 
    Splitting of the scantron data is specific to each scantron machine. The 
    indices used in this function are correct for the scantron machine in the 
    UBC Psychology department as of 2015. Indices need to be adjusted for 
    different machines.
    
    Scantron exams can be finicky. Students who incorrectly fill out scantrons 
    need to be considered. Make sure to manually inspect the text file output 
    by the scantron machine for missing answers before running this. This 
    function does not correct for human error when filling out the scantron.
    
    Parameters
    ----------
    input_scantron : string
        Path to the .txt file produced by the scantron machine.
    correct_answers : list
        A list of strings containing the *correct* exam answers. For example: 
        ["A", "E", "D", "A", B"]. The order must match the order of 
        presentation on the exam (i.e. the first list item must correspond 
        to the first exam question)
    drops : list, optional
        List of integers containing question numbers that should be excluded  
        from calculation of grades. For example: [1, 5] will not include 
        questions 1 and 5 when calculating exam scores.
    item_value : int, optional
        Integer representing how many points each exam question is worth.
    incorrect_threshold : float between [0., 1.], optional
        Poorly performing questions are those where few students got the 
        correct answer. This parameter sets the threshold at which an item is 
        considered poor. For example, a threshold of 0.4 means that a poor 
        item is considered to be one where less than 40% of students 
        chose the correct answer.
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
