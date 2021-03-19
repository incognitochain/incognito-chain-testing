from TestCases.HigwayFork import calculated_and_create_fork

min_blocks_wait_fork = 2  # Chain will be forked after at least {min_blocks_wait_fork} blocks
cID1 = 255
at_transfer_next_epoch = None
num_of_branch = 2
num_of_block_fork = 5
branch_tobe_continue = 1
calculated_and_create_fork(cID1, at_transfer_next_epoch, min_blocks_wait_fork, num_of_branch, branch_tobe_continue,
                           num_of_block_fork)
