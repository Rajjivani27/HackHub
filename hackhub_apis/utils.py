def media_processing(files) -> list:
    files_data = []

    for key,file_list in files:
            if key.startswith('media[') and key.endswith('].files'):
                files_data.append({'files':file_list[0]})

    return files_data


