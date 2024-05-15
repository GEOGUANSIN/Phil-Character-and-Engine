import pandas as pd

open_file = 'test/raw_text'
excel_result_file = 'test/chunked_text.xlsx'

with open(open_file, 'r', encoding='utf-8') as f:
    file_string = f.read()
    file_list = file_string.split('\n')


def remove_by_indices(my_list, indices_to_remove):
    """
    Removes elements from a list based on a provided list of indices.

    Args:
        my_list: The list to modify.
        indices_to_remove: A list of indices to remove (in descending order for efficiency).

    Returns:
        The modified list with elements removed at the specified indices.
    """

    indices_to_remove.sort(reverse=True)  # Sort in descending order for efficiency
    for index in indices_to_remove:
        if 0 <= index < len(my_list):  # Check for valid indices
            del my_list[index]
    return my_list


index_to_be_deleted = []
for i in range(len(file_list)-1):
    paragraph = file_list[i]
    print(paragraph)
    if len(paragraph) < 100:
        index_to_be_deleted.append(i)
    if len(paragraph) < 200:
        print(f'The paragraph: {paragraph} \n')
        response = input('d/uc/dc/n')
        if response == 'd':
            index_to_be_deleted.append(i)
        if response == 'uc':
            file_list[i-1] = file_list[i-1]+'\n'+ file_list[i]
            index_to_be_deleted.append(i)
        if response == 'dc':
            file_list[i + 1] = file_list[i] + '\n' + file_list[i+1]
            index_to_be_deleted.append(i)

print(index_to_be_deleted)

my_list = file_list
indices_to_remove = index_to_be_deleted  # Indices to remove (can be in any order)
modified_list = remove_by_indices(my_list.copy(), indices_to_remove)  # Avoid modifying original list

output_df = pd.DataFrame(modified_list)
output_df.columns = ['paragraph']
output_df.to_excel(excel_result_file)


