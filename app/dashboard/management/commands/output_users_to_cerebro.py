from django.utils import timezone
from economy.models import EncodeAnything
from django.core.management.base import BaseCommand
from dashboard.models import Profile
import json


def get_profiles(limit=3):
    limit = 3

    profiles = Profile.objects.filter(hide_profile=False)
    if limit:
        profiles = profiles[:limit]
    outputs = []
    for profile in profiles:
        output = {
            "pk": profile.pk,
            "handle": profile.handle,
            "persona": profile.cascaded_persona,
            "activity_level": profile.activity_level,
            "reliability": profile.reliability,
            "output_time": timezone.now().strftime('%m/%d/%Y'),
            "last_visit": profile.last_visit.strftime('%m/%d/%Y') if profile.last_visit else None,
            "created_on": profile.created_on.strftime('%m/%d/%Y'),
            "success_rate": profile.success_rate,
            "total_funded_bounties_count": profile.as_dict.get('funded_bounties_count', 0),
            "total_count_bounties_completed": profile.as_dict.get('count_bounties_completed', 0),
            "total_kudos_sent_count": profile.as_dict.get('total_kudos_sent_count', 0),
            "total_kudos_received_count": profile.as_dict.get('total_kudos_received_count', 0),
            "total_grant_created": profile.as_dict.get('total_grant_created', 0),
            "total_grant_contributions": profile.as_dict.get('total_grant_contributions', 0),
            "total_grant_actions": profile.as_dict.get('total_grant_actions', 0),
            "total_tips_sent": profile.as_dict.get('total_tips_sent', 0),
            "total_tips_received": profile.as_dict.get('total_tips_received', 0),
            "total_quest_attempts": profile.as_dict.get('total_quest_attempts', 0),
            "total_quest_success": profile.as_dict.get('total_quest_success', 0),
            "total_bounties_work_started": profile.interested.count(),
            "avg_hourly_rate": profile.avg_hourly_rate,
            "keywords": profile.keywords,
            "works_with_funded": profile.as_dict.get('works_with_funded',[]),
            "works_with_collected": profile.as_dict.get('works_with_collected',[]),
            "organizations": profile.organizations,
            "github_data": profile.data,
            "job_type": profile.job_type,
            "job_salary": profile.job_salary,
            "job_location": profile.job_location,
            "job_salary": profile.job_salary,

        }
        outputs.append(output)
    return outputs


def get_ratings_dict():
    ratings_dict = {
        "target": [],
        "user": [],
        "rating": [],
    }
    from dashboard.models import FeedbackEntry
    fbes = FeedbackEntry.objects.filter(receiver_profile__isnull=False, sender_profile__isnull=False)
    for fbe in fbes:
        ratings_dict['target'].append(fbe.receiver_profile.handle)
        ratings_dict['user'].append(fbe.sender_profile.handle)
        ratings_dict['rating'].append(fbe.rating)

    from dashboard.models import Earning
    for earning in Earning.objects.filter(network='mainnet', to_profile__isnull=False, from_profile__isnull=False):
        ratings_dict['target'].append(earning.from_profile.handle)
        ratings_dict['user'].append(earning.to_profile.handle)
        ratings_dict['rating'].append(4)

    return ratings_dict


class Command(BaseCommand):

    help = 'outputs user data to cerebro ( https://docs.google.com/document/d/12-A8NabEJYzJqJtnHcG4ki1jAJ_K_OM8K_IAGbD8V7Y/edit# )'

    def handle(self, *args, **options):
        n = 24
        from collections import defaultdict
        import pandas as pd
        from surprise import Dataset
        from surprise import Reader
        from surprise import SVD
        from surprise import KNNBaseline
        from surprise import Dataset
        from surprise import accuracy

        def get_top_n(predictions, n=10):
            '''Return the top-N recommendation for each user from a set of predictions.

            Args:
                predictions(list of Prediction objects): The list of predictions, as
                    returned by the test method of an algorithm.
                n(int): The number of recommendation to output for each user. Default
                    is 10.

            Returns:
            A dict where keys are user (raw) ids and values are lists of tuples:
                [(raw item id, rating estimation), ...] of size n.
            '''

            # First map the predictions to each user.
            top_n = defaultdict(list)
            for uid, iid, true_r, est, _ in predictions:
                top_n[uid].append((iid, est))

            # Then sort the predictions for each user and retrieve the k highest ones.
            for uid, user_ratings in top_n.items():
                user_ratings.sort(key=lambda x: x[1], reverse=True)
                top_n[uid] = user_ratings[:n]

            return top_n


        # First train an SVD algorithm on the movielens dataset.
        reader = Reader(rating_scale=(1, 5))

        ratings_dict = get_ratings_dict()

        df = pd.DataFrame(ratings_dict)
        data = Dataset.load_from_df(df[["user", "target", "rating"]], reader)
        trainset = data.build_full_trainset()
        algo = SVD()
        algo.fit(trainset)

        # Than predict ratings for all pairs (u, i) that are NOT in the training set.
        testset = trainset.build_anti_testset()
        predictions = algo.test(testset)

        top_n = get_top_n(predictions, n=n)
        acc = accuracy.rmse(predictions, verbose=True)
        # Print the recommended items for each user
        for uid, user_ratings in top_n.items():
            names = [iid for (iid, _) in user_ratings]
            print(acc, uid, names)
            profile = Profile.objects.get(handle=uid)
            profile.match_profiles = names
            profile.save()

        print("*************************");

        # First, train the algortihm to compute the similarities between items
        trainset = data.build_full_trainset()
        sim_options = {'name': 'pearson_baseline', 'user_based': True}
        algo = KNNBaseline(sim_options=sim_options)
        algo.fit(trainset)

        # Retrieve inner id of the movie Toy Story
        # trainset.to_raw_uid(278)
        for i in range(0, algo.trainset.n_ratings):
            if algo.trainset.knows_item(i):
                inner_id = i
                name = algo.trainset.to_raw_iid(inner_id)

                neighbors = algo.get_neighbors(inner_id, k=n)
                neighbors = [trainset.to_raw_uid(i) for i in neighbors]
                print(f'The 10 nearest neighbors of {name} are: {neighbors}')
                profile = Profile.objects.get(handle=name)
                profile.related_profiles = neighbors
                profile.save()


        # TODO: How to get the top-N recommendations for each user
        # https://surprise.readthedocs.io/en/stable/FAQ.html#how-to-get-the-top-n-recommendations-for-each-user
        # TODO: How to get the k nearest neighbors of a user (or item)
        # https://surprise.readthedocs.io/en/stable/FAQ.html#how-to-get-the-k-nearest-neighbors-of-a-user-or-item
        # Here’s an example to find out how the user E would rate the movie 2:
        # from https://realpython.com/build-recommendation-engine-collaborative-filtering/
        # prediction = algo.predict('E', 2)

