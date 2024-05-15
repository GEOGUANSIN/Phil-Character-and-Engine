import pandas as pd
from openai import OpenAI
from io import StringIO
import ollama

# remember to change the 1.paragraph file 2.the initial context 3. index number 4. theme index number


text_excel = 'test/chunked_text.xlsx'
output_excel = 'test/test_rag_data.xlsx'
model = 'gpt-3.5-turbo'
api_key = 'your_api_key'

head_paragraphs_file = 'test/head_paragraphs'
template_goal_init_file = 'New_Prompt_Template/goal_initiation'
template_context_file = 'New_Prompt_Template/context_update'
template_context_shorten = 'New_Prompt_Template/context_shorten'
template_theme_file = 'New_Prompt_Template/theme_division'
template_question_making_file = 'New_Prompt_Template/question_making'
template_question_element_file = 'New_Prompt_Template/question_element_breakdown'
template_question_mode_file = 'New_Prompt_Template/question_mode_classification'
role_file = 'test/role'
author_file = 'test/author'
source_file = 'test/source'
initial_context_file = 'test/initial_context'
initial_text_index = 0 # the end index of the existing paragraphs + 1
initial_index = 9  # the end index


text_data = pd.read_excel(text_excel)

with open(head_paragraphs_file, 'r', encoding='utf-8') as f:
    head_paragraphs = f.read()
with open(template_goal_init_file, 'r', encoding='utf-8') as f:
    prompt_template_goal_init = f.read()
with open(template_theme_file, 'r', encoding='utf-8') as f:
    prompt_template_theme_division = f.read()
with open(template_context_file, 'r', encoding='utf-8') as f:
    prompt_template_context_update = f.read()
with open(template_context_shorten, 'r', encoding='utf-8') as f:
    prompt_template_context_shorten = f.read()
with open(template_question_making_file, 'r', encoding='utf-8') as f:
    prompt_template_question_making = f.read()
with open(template_question_element_file, 'r', encoding='utf-8') as f:
    prompt_template_question_element = f.read()
with open(template_question_mode_file, 'r', encoding='utf-8') as f:
    prompt_template_question_mode = f.read()
with open(role_file, 'r', encoding='utf-8') as f:
    role = f.read()
with open(author_file, 'r', encoding='utf-8') as f:
    author = f.read()
with open(source_file, 'r', encoding='utf-8') as f:
    source = f.read()
with open(initial_context_file, 'r', encoding='utf-8') as f:
    initial_context = f.read()

client = OpenAI(
    api_key=api_key
)


def make_ollama_request(_content_prompt, _role_prompt='', _model='llama3'):
    if _role_prompt is not None:
        _role_prompt = 'role:' + _role_prompt + '\n user:'

    response = ollama.chat(
        model='llama3',
        messages=[{
            'role': 'user',
            'content': _role_prompt + _content_prompt}],
    )

    output = response['message']['content']
    print(output)
    return output



def make_open_ai_request(_user_prompt, _system_prompt='', _model=model):
    message = [
        {
            "role": "system",
            "content": _system_prompt,
        },
        {
            "role": "user",
            "content": _user_prompt,
        }
    ]
    completion = client.chat.completions.create(
        model=_model,
        messages=message
    )
    _answer = completion.choices[0].message.content
    return _answer


def response_cleaning(string_thing):
    if 'format:' in string_thing:
        string_thing = string_thing.split('format:')[1]
    string_thing = string_thing.replace("```python", "")
    string_thing = string_thing.replace("```", "")
    string_thing = string_thing.replace("```", "").replace('yaml\n', '').replace('yaml', '')
    string_thing = string_thing.replace('\nrelevant_elements = ', '')
    string_thing = string_thing.replace('relevant_elements = ', '').replace('\nrelevant_elements', '').replace('relevant_elements', '')
    string_thing = string_thing.replace('\nelements_list = ', '')
    string_thing = string_thing.replace('elements_list = ', '').replace('elements_list', '')
    string_thing = string_thing.replace('{"main subject": "Set temperature"', '')
    string_thing = string_thing.replace('```jsonl', '').replace('```', '').replace('jsonl', '').replace('json', '')
    if ('[{' in string_thing) and ('}]' in string_thing):
        string_thing = string_thing.split('[{')[1].split('}]')[0]
        string_thing = "[{" + f'{string_thing}' + "}]"
    if ('[' in string_thing) and (']' in string_thing):
        string_thing = string_thing.split('[')[1].split(']')[0]
        string_thing = "[" + f'{string_thing}' + "]"
    # string_thing = string_thing.replace('\n    {', '').replace('    {', '{')
    # string_thing = string_thing.replace('"', "'")
    # string_thing = string_thing.replace(',', '，').replace('"，', '",').replace("]，", '],').replace("}，", '},')
    return string_thing


def zip_list(list1, list2):
    result = [(x, y) for x, y in zip(list1, list2)]
    return result


def jsonl_string_cleaning(jsonl_string):
    jsonl_string_0 = jsonl_string.replace('```jsonl', '').replace('```', '').replace("'", '"')
    jsonl_clean_string = jsonl_string_0.replace(',', '，').replace('"，', '",').replace("]，", '],').replace("}，", '},')
    return jsonl_clean_string


def mode_translation(mode_string):
    mode_string = mode_string.replace('A', 'What-question')
    mode_string = mode_string.replace('B', 'When-question')
    mode_string = mode_string.replace('C', 'How-question')
    mode_string = mode_string.replace('D', 'Why-question')
    return mode_string


def add_new_row_to_excel(new_row_data, _output_excel=output_excel):
    df = pd.read_excel(_output_excel)
    df = df._append(new_row_data, ignore_index=True)
    df.to_excel(_output_excel, index=False)


def eval_list(string: str) -> list:
    list_raw = string.split('[')[1].split(']')[0]
    list_ = eval(f'[{list_raw}]')
    return list_


def eval_dict(string: str) -> dict:
    dict_raw = string.split('{')[1].split('}')[0]
    dict_ = eval('{' + f'{dict_raw}' + '}')
    return dict_


error_count = 0
context = initial_context

# goal initiation
prompt_goal_init_0 = prompt_template_goal_init.replace('$@role', role)
prompt_goal_init = prompt_goal_init_0.replace('$@head_paragraphs', head_paragraphs)
goal = []
through = False
while not through:
    try:
        goal_list = eval_list(make_ollama_request(prompt_goal_init))
        # goal_list = eval(make_ollama_request(prompt_goal_init))
        print(f"goal_list: {goal_list}")
        goal = 'The goal of reading the article is to understand the following question:\n' \
               + '\n'.join(f"{index + 1}. {question}" for index, question in enumerate(goal_list))
        through = True
    except Exception as e:
        error_count += 1
        print(e)

k = initial_index
for index, row in text_data.iterrows():
    paragraph_index = index + initial_text_index
    j = 0

    # context_update
    paragraph = row['paragraph']
    prompt_context_update_0 = prompt_template_context_update.replace('$@paragraph', paragraph)
    prompt_context_update_1 = prompt_context_update_0.replace('$@context', context)
    prompt_context_update = prompt_context_update_1.replace('$@role', role)
    through = False
    while not through:
        try:
            context_triple = eval_dict(make_ollama_request(prompt_context_update))
            context = context_triple['updated context']
            through = True
        except Exception as e:
            error_count += 1
            print(e)
    j += 1
    print(j)

    # context_summarization
    if len(context) > 2000:
        through = False
        prompt_context_shorten_0 = prompt_template_context_shorten.replace('$@context', context)
        prompt_context_shorten_1 = prompt_context_shorten_0.replace('$@goal', goal)
        prompt_context_shorten = prompt_context_shorten_1.replace('$@role', role)
        while not through:
            try:
                context = make_ollama_request(prompt_context_shorten)
                if len(context) < 3000:
                    through = True
            except Exception as e:
                error_count += 1
                print(e)
    j += 1
    print(j)

    # theme_division
    prompt_theme_division_0 = prompt_template_theme_division.replace('$@context', str(context))
    prompt_theme_division_1 = prompt_theme_division_0.replace('$@goal', goal)
    prompt_theme_division_2 = prompt_theme_division_1.replace('$@role', role)
    prompt_theme_division = prompt_theme_division_2.replace('$@paragraph', paragraph)
    through = False
    theme_list = []
    abstract_list = []
    while not through:
        try:
            theme_abstract_jsonl_string = make_ollama_request(prompt_theme_division)
            theme_abstract_jsonl_string = response_cleaning(theme_abstract_jsonl_string)
            # print(theme_abstract_jsonl_string)
            # theme_abstract_jsonl_clean_string = jsonl_string_cleaning(theme_abstract_jsonl_string)
            df_theme_abstract = pd.read_json(StringIO(theme_abstract_jsonl_string))
            theme_list = df_theme_abstract['theme'].tolist()
            abstract_list = df_theme_abstract['abstract'].tolist()
            through = True
        except Exception as e:
            error_count += 1
            print(e)
    j += 1
    print(j)

    for i in range(len(theme_list)):
        theme_index = i
        theme = theme_list[i]
        abstract = abstract_list[i]

        # making questions list
        question_list = []
        prompt_question_making_0 = prompt_template_question_making.replace('$@abstract', abstract)
        prompt_question_making = prompt_question_making_0.replace('$@context', str(context))
        through = False
        while not through:
            try:
                output_question_list = response_cleaning(make_ollama_request(prompt_question_making))
                # print(f"\noutput_question_list: {output_question_list}")
                question_list = eval_list(output_question_list)
                if type(question_list) == list:
                    through = True
            except Exception as e:
                error_count += 1
                print(e)
        j += 1
        print(j)


        # question mode and element
        prompt_question_mode = prompt_template_question_mode.replace('$@question_list', str(question_list))
        prompt_question_element = prompt_template_question_element.replace('$@question_list', str(question_list))
        standard_question_list = []
        through = False
        while not through:
            try:
                question_mode_string = response_cleaning(mode_translation(make_ollama_request(prompt_question_mode)))
                # print(f"\nquestion_mode_string: {question_mode_string}")
                question_mode_list = eval_list(question_mode_string)
                question_element_string = response_cleaning(make_ollama_request(prompt_question_element))
                # print(f"\nquestion_element_string: {question_element_string}")
                question_element_list = eval_list(question_element_string)
                standard_question_list = zip_list(question_mode_list, question_element_list)
                if type(standard_question_list) == list:
                    through = True
            except Exception as e:
                error_count += 1
                print(e)
        j += 1
        print(j)


        k += 1
        answer = {
            "index": k,
            "theme_index": theme_index,
            "theme": theme,
            "abstract": abstract,
            "normal_questions_list": question_list,
            "questions_list": standard_question_list,
            "text": paragraph,
            "text_index": paragraph_index,
            "author": author,
            "source_and_intro": source,
            "goal": goal,
            "context": context,
            "role": role
        }

        print(f"answer:{answer}")
        print(f"error_count:{error_count}")
        add_new_row_to_excel(answer)
