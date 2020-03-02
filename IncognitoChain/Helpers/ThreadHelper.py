def wait_threads_to_complete(thread_list):
    # wait for all sending thread to complete
    for thread in thread_list:
        thread.join()
