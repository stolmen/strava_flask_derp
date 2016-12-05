"""
    Miscellaneous utilities
"""


def sum_of_kudos_in_activity(activity_list):
    kudos_sum = 0    
    for activity in activity_list:
        kudos_sum += activity['kudos_count']
    return kudos_sum
