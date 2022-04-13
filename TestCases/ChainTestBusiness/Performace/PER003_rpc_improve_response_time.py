from Objects.NodeObject import Node


def t_rpc_response_time():
    """
    MUST only run this test on fullnode.
    :return:
    """
    node = Node(address='localhost', rpc_port=9334)
    # node = Node(address='test-node.incognito.org', rpc_port=9334)

    private_key = '112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA'
    shard_id = 0
    token_id = '4129f4ca2b2eba286a3bd1b96716d64e0bc02bd2cc1837776b66f67eb5797d79'

    res = dict()
    res['list_privacy_custom_token'] = node.explore_rpc().list_privacy_custom_token()
    res['list_privacy_custom_token_by_shard'] = node.explore_rpc().list_privacy_custom_token_by_shard(shard_id)
    res['get_list_privacy_custom_token_balance'] = node.explore_rpc().get_list_privacy_custom_token_balance(private_key)
    res['get_balance_privacy_custom_token'] = node.explore_rpc().get_balance_privacy_custom_token(private_key, token_id)
    res['privacy_custom_token'] = node.explore_rpc().privacy_custom_token(token_id)
    for f in res.keys():
        time = res[f].response_time()
        size = res[f].size()
        print(f'''
            {f} : 
                res time  : {time} s
                size      : {size / 1024} kb
                size/time : {size / time / 1024} kb/s ''')
