import pandas as pd

excel_open_file = 'test/test_rag_data.xlsx'
excel_result_file = 'test/test_rag_questions_and_index.xlsx'

theme_data = pd.read_excel(excel_open_file)

answer_df = pd.DataFrame({'question': ['questions'], 'question_mode': ['question_mode'], 'theme_index': ['index'], 'source': ['source_and_intro']})
for index, row in theme_data.iterrows():
    print(f"type(row['questions_list'])): {type(row['questions_list'])}")
    through = False
    question_list = []
    while not through:
        try:
            question_list = eval(row['questions_list'])
            print(question_list)
            through = True
        except Exception as e:
            print(e)
    for question_item in question_list:
        print(f'question_item:{question_item}')
        print(f'type(question_item):{type(question_item)}')
        question_mode, question = eval(str(question_item))
        try:
            question = eval(str(question))
            key_terms = list(question.values())[-1]
            subject = [str(list(question.values())[0])]
            question_terms = subject + key_terms + [row['theme']]
            df = pd.DataFrame({'question': [question_terms], 'question_mode': [question_mode], 'theme_index': [row['index']], 'source': [row['source_and_intro']]})
            print(df)
            answer_df = pd.concat([answer_df, df])
        except Exception as e:
            print(e)

answer_df.reset_index(drop=True, inplace=True)
answer_df.to_excel(excel_result_file)