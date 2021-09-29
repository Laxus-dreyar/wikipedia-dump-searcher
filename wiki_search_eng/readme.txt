To index the dump, run
    python3 index.py <path_to_dump> <path_to_inverted_index_folder>
    for eg,
        python3 index.py /home/mrinal/dump.xml ./inverted_index/

To get the titles for search queries, run
    python3 search.py <path_to_inverted_index_folder> <path_to_querys>
    for eg,
        python3 search.py ./inverted_index/ ./queries.txt
    
    note that the answers will be written in queries_op.txt

Please note that the stats mentioned in stats.txt are extrapolations of the stats that i got from running the index for a considerable amount of time as the entire dump could not be indexed due to time contraints