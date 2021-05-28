def chunk_dict(data,
               chunk=10000,
               max_tasks=None,):

    data_list = []
    curr_dict = {}
    for k, v in data.items():

        if len(curr_dict) >= chunk:
            data_list.append(curr_dict)
            curr_dict = []

        if max_tasks is not None and len(data_list) >= max_tasks:
            break

        curr_dict[k] = v

    if len(curr_dict) > 0:
        data_list.append(curr_dict)

    return data_list
