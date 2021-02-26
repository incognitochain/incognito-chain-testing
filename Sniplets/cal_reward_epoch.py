from time import sleep

from Helpers import TestHelper
from Helpers.Logging import INFO
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import SUT

beacon_list = [
    Account(
        '112t8rncBDbGaFrAE7MZz14d2NPVWprXQuHHXCD2TgSV8USaDFZY3MihVWSqKjwy47sTQ6XvBgNYgdKH2iDVZruKQpRSB5JqxDAX6sjMoUT6'),
    Account(
        '112t8rnfXYskvWnHAXKs8dXLtactxRqpPTYJ6PzwkVHnF1begkenMviATTJVM6gVAgSdXsN5DEpTkLFPHtFVnS5RePi6aqTSth6dP4frcJUT'),
    Account(
        '112t8rngZ1rZ3eWHZucwf9vrpD1DNUAmrTTARSsptNDFrEoHv3QsDY3dZe8LXy3GeKXmeso8nUPsNwUM2qmZibQVXxGzstF4vZsYzJ83scFL'),
    Account(
        '112t8rnpXg6CLjvBg2ZiyMDgpgQoZuAjYGzbm6b2eXVSHUKjZUyb2LVJmJDPw4yNaP5M14DomzC514joTH3EVknRwnnGViWuH2HJuN6cpNhz')]

committee_dict = {
    "0": [
        Account(
            '112t8rnqijhT2AqiS8NBVgifb86sqjfwQwf4MHLMAxK3gr1mwxMaeUWQtR1MfxHscrKQ2MsyQMvJ3LEu49LEcZzTzoJCkCiewQ9p6wN5SrG1'),
        Account(
            '112t8rnud1R3of9rPkdKHWy8mQ5gMpXuBjLGhVrNurvHC93fF6qfiaEC8Nf7AHRbgrn1KF33akoNMNqUEUdSU7caXYvRL4uT58fhCuDV2Qs8'),
        Account(
            '112t8rnw7XyoehhKAUbNTqtVcda1eki89zrD2PfGMBKoYHvdE94ApWvXDtJvgotQohRot8yV52RZz2JjPtYGh4xsxb3gahn7RRWocEtW2Vei'),
        Account(
            '112t8ro1sHxz5xDkTs9i9VHA4cXVb5iqwCq2H2ffYYbGRh2wUHSHRRbnSQEMSnGiMvZAFLCccNzjZV9bSrphwGxxgtskVcauKNdgTEqA9bsf'),
        Account(
            '112t8ro424gNfJkKqDj25PjgWqCFTgG83TRERX1djUVr2wgJB6Lwk7NFi4pU8KxWSHsb4xK7UwPVYJ48FEGTzrB9jM58WfyvaJGCsT83jfNs'),
        Account(
            '112t8ro719sBgnX2GouVjLEZUvVwaepg8FkG35GtrFiFHeuE3y47PjXBbxHQdX1z87AAtEH5WCMZ8GUbhaZL3DbJuLqj7AAxGoc85damvB4J')
    ],

    "1": [
        Account(
            '112t8rncy1vEiCMxvev5EkUQyfH9HLeManjS4kbcsSiMgp4FEiddsiMunhYL2pa8wciCAWxYtt9USgCv21fe2PkSxfnRkiq4AmDvJe33wtgV'),
        Account(
            '112t8rndMXjgDEGkuUmVedQxVYuZsQK5UvM9ZR1aZximBuNNJKpBn9j93MRqLBS17mHoCdLQNMmoYyuERZ1M3pRMG8SQj3NraHsG9eZPbbRK'),
        Account(
            '112t8rngznzWowvtXKyTnE9avawQGJCVgfJounHDT5nWucoVFv43TYu9PyjiGpPXXXQbCVEzxxCSfDmPNEBknK5B8n5qFiaddStg2M9pCYkZ'),
        Account(
            '112t8rnk4jduDzQGcmzKXr6r1F69TeQtHqDBCehDXPpwQTo7eDkEKFGMDGar46Jy4gmqSZDgwyUwpnxGkCnE2oEXmQ5FQpQJ4iMpDqLkgzwy'),
        Account(
            '112t8rnkSY1EtXtfZNGTKU6CFhfrdQ2YqLbLpfFEUGzVfoQeC6d47M5jWwv542aHJgEdtBKxmr2aikjxibL75rqGXEyKfUPXg1yp3xnCpL7D'),
        Account(
            '112t8rnmCktTnBnX866sSj5BzU33bUNZozJRes9xL7GPqSTQX9gsqG3qkiizsZuzV7BFs7CtpqNhcWfEMUZkkT7JnzknDB49jD2UBUemdnbK')
    ]
}


def get_reward(list_acc):
    list_amount = []
    for acc in list_acc:
        amount = acc.stk_get_reward_amount()
        list_amount.append(amount)
    return list_amount


def print_reward(list_amount_new, list_amount_old, name):
    for i in range(0, len(list_amount_new)):
        new_reward = list_amount_new[i]
        old_reward = list_amount_old[i]
        print(
            f'{name}{i} reward : {new_reward} - {old_reward} = {new_reward - old_reward}')


def watch_dog():
    get_latest_epoch = SUT().help_get_current_epoch
    previous_epoch = latest_epoch = get_latest_epoch()
    s0_previous_reward = get_reward(committee_dict['0'])
    s1_previous_reward = get_reward(committee_dict['1'])
    b_previous_reward = get_reward(beacon_list)

    while True:

        if previous_epoch != latest_epoch:
            s0_latest_reward = get_reward(committee_dict['0'])
            s1_latest_reward = get_reward(committee_dict['1'])
            b_latest_reward = get_reward(beacon_list)

            current__epoch_height_start = TestHelper.ChainHelper.cal_first_height_of_epoch(latest_epoch)
            previous_epoch_height_start = TestHelper.ChainHelper.cal_first_height_of_epoch(previous_epoch)

            INFO(
                f"epoch: {previous_epoch}, from height {previous_epoch_height_start} to {current__epoch_height_start - 1}")
            print_reward(b_latest_reward, b_previous_reward, 'Beacon')
            print('---------')
            print_reward(s0_latest_reward, s0_previous_reward, "Shard0")
            print('---------')
            print_reward(s1_latest_reward, s1_previous_reward, "Shard1")
            print()

            s0_previous_reward = s0_latest_reward
            s1_previous_reward = s1_latest_reward
            b_previous_reward = b_latest_reward

            previous_epoch = latest_epoch

        sleep(10)
        latest_epoch = get_latest_epoch()
