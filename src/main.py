import random
import pandas as pd
import statistics
import numpy as np
import matplotlib.pyplot as plt
import math


num_sims = 20
num_women = 333
num_men = 667
profiles_per_day_men = 200
profiles_per_day_women = 100
like_percentage_men = 0.25  #  0.46
like_percentage_women = 0.25  #  0.14
include_attractiveness = False

class User:
    def __init__(self, id, gender, profiles_per_day, like_percentage, include_attractiveness):
        self.id = id
        self.gender = gender
        self.profiles_per_day = profiles_per_day
        self.like_percentage = like_percentage
        self.likes = 0
        self.matches = 0
        self.swipes = 0  # nr of times the profile was swiped by other users
        self.attractiveness = random.random()
        self.users_like_sent = []
        self.users_like_received = []
        self.include_attractiveness = include_attractiveness

    def swipe(self, other_user):
        other_user.swipes += 1
        random_number = random.random()
        prob = self.get_like_prob(other_user)
        # prob = other_user.attractiveness * self.like_percentage
        if random_number <= prob:
            # Like:
            other_user.likes += 1
            other_user.users_like_received.append(self.id)
            self.users_like_sent.append(other_user.id)
            if self.id in other_user.users_like_sent:
                # Match
                self.matches += 1
                other_user.matches += 1

    def get_like_prob(self, other_user):
        if user.include_attractiveness:
            like_prob = other_user.attractiveness ** (1/self.like_percentage-1)
        else:
            like_prob = self.like_percentage
        return like_prob

    def get_like_prob_old(self, other_user):
        if self.gender == 'MALE':
            x=1
            # Assume that top 20% most attractive users get 80% of likes
            prob_0_80 = self.like_percentage * 0.25
            prob_80_100 = self.like_percentage * 4
            if prob_0_80 + prob_80_100 <= 1:
                # 80-20 rule is possible
                prob_0 = 0
                prob_80 = prob_0_80 * 2
                if other_user.attractiveness < 0.8:
                    like_prob = prob_0 + (other_user.attractiveness/ 0.8) * (prob_80 - prob_0)
                else:
                    prob_100 = prob_80 + (prob_80_100 - prob_80) * 2
                    if prob_100>1:
                        # continuous distribution is not possible. Lower prob_100 on 100% and raise prob_80
                        prob_100 = 1
                        prob_80 = 1-(1-prob_80_100)*2
                    like_prob = prob_80 + ((other_user.attractiveness - 0.8) / 0.2) * (prob_100 - prob_80)
            else:
                # 80-20 rule is not possible. top 20% users get 100% like percentage, bottom 80% get the rest
                prob_80_100 = 1
                prob_0_80 = (self.like_percentage - 0.2)/0.8
                if other_user.attractiveness < 0.8:
                    prob_80 = 1
                    prob_0 = prob_80 - (prob_80-prob_0_80)*2
                    if prob_0 < 0:
                        # raise prob_0, lower prob_80
                        prob_0 = 0
                        prob_80 = prob_0_80 * 2
                    like_prob = prob_0 + (other_user.attractiveness / 0.8) * (prob_80 - prob_0)
                else:
                    like_prob = 1
        return like_prob

# Initialize KPIs
user_gender_total = []
user_likes_total = []
user_matches_total = []
user_attractiveness_total = []

user_likes_means = []
user_matches_means = []

user_likes_medians = []
user_matches_medians = []

# Run Sims
for sim in range(0, num_sims):
    print("Sim %s/%s" % (str(sim+1), num_sims))
    users_female = [User(user, 'FEMALE', profiles_per_day_women, like_percentage_women, include_attractiveness) for user in range(0, num_women)]
    users_male = [User(user, 'MALE', profiles_per_day_men, like_percentage_men, include_attractiveness) for user in range(num_women, num_women + num_men)]
    users = users_female + users_male

    # Match users:
    users_female_swipes = [(user.id, user.swipes) for user in users_female]
    users_male_swipes = [(user.id, user.swipes) for user in users_male]
    for user in users_female:
        users_male_swipes = [(user.id, user.swipes) for user in users_male]
        users_male_swipes.sort(key=lambda x: x[1])
        swipe_count = 0
        for (user_male_id, user_male_swipes) in users_male_swipes:
            user_male = users[user_male_id]
            if swipe_count < profiles_per_day_women:
                user.swipe(user_male)
            else:
                break
            swipe_count += 1
    for user in users_male:
        users_female_swipes = [(user.id, user.swipes) for user in users_female]
        users_female_swipes.sort(key=lambda x: x[1])
        swipe_count = 0
        # start with other users who already liked the user:
        for user_female_id in user.users_like_received:
            user_female = users[user_female_id]
            if swipe_count < profiles_per_day_men:
                user.swipe(user_female)
            else:
                break
            swipe_count += 1
        # remaining users:
        for (user_female_id, user_female_swipes) in users_female_swipes:
            if swipe_count < profiles_per_day_men:
                if user_female_id not in user.users_like_received:
                    user_female = users[user_female_id]
                    user.swipe(user_female)
                    swipe_count += 1
            else:
                break

    # Update KPIs:
    user_gender = [user.gender for user in users]
    user_likes = [user.likes for user in users]
    user_matches = [user.matches for user in users]
    user_attractiveness = [user.attractiveness for user in users]

    user_gender_total += user_gender
    user_likes_total += user_likes
    user_matches_total += user_matches
    user_attractiveness_total += user_attractiveness

    user_likes_means.append(np.mean(user_likes))
    user_matches_means.append(np.mean(user_matches))

    user_likes_medians.append(np.median(user_likes))
    user_matches_medians.append(np.median(user_matches))


def convert_bins_to_size(data_range, X):
    min_val = int(min(data_range))
    max_val = int(max(data_range))
    new_bins = list(range(min_val, max_val + X, X))
    return new_bins

# plt.figure(figsize=(12, 6))
# data_range = range(int(min(male_likes_total)), int(max(female_likes_total)) + 2)
# new_bins = convert_bins_to_size(data_range, 10)
# plt.hist(female_likes_total, bins=new_bins, alpha=0.5, label='Female Likes')
# plt.hist(male_likes_total, bins=new_bins, alpha=0.5, label='Male Likes')
# plt.title("Average Number of Likes and Matches")
# plt.xlabel("Values")
# plt.ylabel("Frequency")
# plt.legend(loc='upper right')
# plt.show()


df = pd.DataFrame()
df['gender'] = user_gender_total
df['attractiveness'] = user_attractiveness_total
df['likes'] = user_likes_total
df['matches'] = user_matches_total
df.to_csv('../results/user_data.csv')
