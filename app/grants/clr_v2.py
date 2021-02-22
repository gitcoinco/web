# -*- coding: utf-8 -*-
"""Define the Grants application configuration.

Copyright (C) 2020 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from django.utils import timezone
from grants.clr import fetch_data

import scipy
import scipy.sparse
import numpy as np
import time

def pairwise_clr_match_sparse(contribs, trust, m):
    participant_overlap = (contribs.T.sqrt()@ contribs.sqrt()).todense()
    k = m / (m+participant_overlap)
    # No self-subsidy
    np.fill_diagonal(k, 0)
    tiled = np.tile(trust, (trust.shape[0],1))
    max_pairwise_trust = np.maximum(tiled, tiled.T)

    # annoying, but we can't use einsum for sparse so will have to do this row by row
    def row_result(row):
        return ((row.T @ row).multiply( np.multiply(k,max_pairwise_trust)).sum())

    return np.array([row_result(contribs[r:r+1,:].sqrt()) for r in range(contribs.shape[0])])


# project_user_contrib tuples is a list of [project_id, user_id, contribution_amount] tuples
# project_id and user_id should start at 0
def load_sparse_matrix(project_user_contrib_tuples, num_projects, num_users):
    data = [x[2] for x in project_user_contrib_tuples]
    row = [x[0] for x in project_user_contrib_tuples]
    col = [x[1] for x in project_user_contrib_tuples]

    return scipy.sparse.csc_matrix((data, (row,col)), shape=(num_projects,num_users))



def predict_clr(save_to_db=False, from_date=None, clr_round=None, network='mainnet', only_grant_pk=None):
    # setup
    start_time = time.time()
    clr_calc_start_time = timezone.now()
    debug_output = []

    # one-time data call
    total_pot = float(clr_round.total_pot)
    v_threshold = float(clr_round.verified_threshold)
    uv_threshold = float(clr_round.unverified_threshold)

    grants, contributions = fetch_data(clr_round, network)

    easy_contrib_np = np.array([[1.,4],[1.,1.]])
    easy_trust_np = np.array([1,.5])
    # Trust is trust score indexed by user
    # M is a parameter in the pairwise QF algo
    m = 1

    # [project_id, user_id, contribution_amount]
    project_user_contrib_tuples = contributions.values_list('subscription__grant__id', 'profile_for_clr__id', 'subscription__amount_per_period_usdt', )
    run_time = time.time() - start_time
    print(f"pulled {len(project_user_contrib_tuples)} contributions in {round(run_time, 2)}s")
    start_time = time.time()
    project_user_contrib_tuples = [(int(ele[0]), int(ele[1]), int(ele[2])) for ele in project_user_contrib_tuples]
    contrib = [x[2] for x in project_user_contrib_tuples]
    project = [x[0] for x in project_user_contrib_tuples]
    user = [x[1] for x in project_user_contrib_tuples]

    user_set = set(user)
    user_to_idx = {x:i for (i,x) in enumerate(user_set)}

    project_set = set(project)
    project_to_idx = {x:i for (i,x) in enumerate(project_set)}
    idx_to_project = {i:x for (i,x) in enumerate(project_set)}

    processed_contribs = [(project_to_idx[p], user_to_idx[u], c) for (p,u,c) in zip(project, user, contrib)]

    sparse_matrix = load_sparse_matrix(processed_contribs, len(project_set), len(user_set))
    matches = pairwise_clr_match_sparse(sparse_matrix, np.array([1.]*len(user_set)), 1)
    project_id_match_pairs = [(idx_to_project[i], matches[i]) for i in range(len(project_set))]

    run_time = time.time() - start_time
    print(f"ran calcs {round(run_time, 2)}s")

    return project_id_match_pairs

