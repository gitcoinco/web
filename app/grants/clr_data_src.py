from django.db import connection

from grants.models import Contribution, Grant, GrantCollection
from townsquare.models import SquelchProfile


def fetch_grants(clr_round, network='mainnet'):
    '''
        Fetch grants that are included in the provided clr_round

        Args:
            network     :   mainnet | rinkeby
            clr_round   :   GrantCLR
        Returns:
            grants      :   list of grants based on clr_type

    '''

    grant_filters = clr_round.grant_filters
    collection_filters = clr_round.collection_filters

    grants = clr_round.grants.filter(network=network, hidden=False, active=True, is_clr_eligible=True, link_to_new_grant=None)

    if grant_filters:
        # Grant Filters (grant_type, category)
        grants = grants.filter(**grant_filters)
    elif collection_filters:
        # Collection Filters
        grant_ids = GrantCollection.objects.filter(**collection_filters).values_list('grants', flat=True)
        grants = grants.filter(pk__in=grant_ids)

    return grants


def fetch_contributions(clr_round, network='mainnet'):
    '''
        Fetch contributions that are included in the provided clr_round

        Args:
            network       :   mainnet | rinkeby
            clr_round     :   GrantCLR
        Returns:
            contributions :   contributions data object

    '''

    clr_start_date = clr_round.start_date
    clr_end_date = clr_round.end_date
    grant_filters = clr_round.grant_filters
    subscription_filters = clr_round.subscription_filters
    collection_filters = clr_round.collection_filters

    contributions = Contribution.objects.prefetch_related('subscription', 'profile_for_clr').filter(
        match=True,
        created_on__gte=clr_start_date,
        created_on__lte=clr_end_date,
        success=True,
        subscription__network='mainnet'
    ).nocache()

    if subscription_filters:
        contributions = contributions.filter(**subscription_filters)

    # ignore profiles which have been squelched
    profiles_to_be_ignored = SquelchProfile.objects.filter(active=True).values_list('profile__pk')
    contributions = contributions.exclude(profile_for_clr__in=profiles_to_be_ignored)

    return contributions


def fetch_summed_contributions(grants, clr_round, network='mainnet'):
    '''
        Aggregated contributions grouped by grant and contributor

        args:
            grants      :   Grants (to fetch contribs for)
            clr_round   :   GrantCLR
            network     :   mainnet | rinkeby
        returns:
            aggregated contributions by pair nested dict
                {
                    grant_id (str): {
                        user_id (str): aggregated_amount (float)
                    }
                }
            dictionary of profile_ids and trust scores
                {user_id (str): trust_score (float)}
    '''

    multiplier = clr_round.contribution_multiplier
    clr_start_date = clr_round.start_date
    clr_end_date = clr_round.end_date

    # only consider contribs from current grant set
    grantIds = ''
    for i in range(len(grants)):
        grantIds += "'" + str(grants[i].id) + "'" + (', ' if i+1 != len(grants) else '')

    # collect contributions with a groupBy sum query
    summedContribs = f'''
        -- group by ... sum the contributions $ value for each user
        SELECT
            grants.use_grant_id as grant_id,
            grants_contribution.profile_for_clr_id as user_id,
            SUM((grants_contribution.normalized_data ->> 'amount_per_period_usdt')::FLOAT * {float(multiplier)}),
            MAX(dashboard_profile.as_dict ->> 'trust_bonus')::FLOAT as trust_bonus
        FROM grants_contribution
        INNER JOIN dashboard_profile ON (grants_contribution.profile_for_clr_id = dashboard_profile.id)
        INNER JOIN grants_subscription ON (grants_contribution.subscription_id = grants_subscription.id)
        RIGHT JOIN (
            SELECT
                grants_grant.id as grant_id,
                (
                    CASE
                    WHEN grants_grant.defer_clr_to_id IS NOT NULL THEN grants_grant.defer_clr_to_id
                    ELSE grants_grant.id
                    END
                ) as use_grant_id
            FROM grants_grant
        ) grants ON ((grants_contribution.normalized_data ->> 'id')::FLOAT = grants.grant_id)
        WHERE (
            grants_contribution.normalized_data ->> 'id' IN ({grantIds}) AND
            grants_contribution.created_on >= '{clr_start_date}' AND
            grants_contribution.created_on <= '{clr_end_date}' AND
            grants_contribution.match = True AND
            grants_subscription.network = '{network}' AND
            grants_contribution.success = True AND
            (grants_contribution.normalized_data ->> 'amount_per_period_usdt')::FLOAT >= 0 AND
            NOT (
                grants_contribution.profile_for_clr_id IN (
                    SELECT squelched.profile_id FROM townsquare_squelchprofile squelched WHERE squelched.active = True
                ) AND grants_contribution.profile_for_clr_id IS NOT NULL
            )
        )
        GROUP BY grants.use_grant_id, grants_contribution.profile_for_clr_id;
    '''

    # open cursor and execute the groupBy sum for the round
    with connection.cursor() as cursor:
        curr_agg = {}
        trust_dict = {}
        # execute to populate shared state for the round
        cursor.execute(summedContribs)
        for _row in cursor.fetchall():
            if not curr_agg.get(_row[0]):
                curr_agg[_row[0]] = {}
            trust_dict[_row[1]] = _row[3]
            curr_agg[_row[0]][_row[1]] = _row[2]

    return curr_agg, trust_dict
