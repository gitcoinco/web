# Running User Directory Elastic Search locally

Elastic Search will automatically start up on `docker-compose up`
Additional configuration options are available in the elasticsearch.yml file.

*Setup Steps*

1. Install the Materialized View in your database. (see below)
2. Add an ENV for the HAYSTACK_ELASTIC_SEARCH_URL variable to your app/app/.env file, `HAYSTACK_ELASTIC_SEARCH_URL=http://elasticsearch:9200`
3. Restart Gitcoin Web with updated env variables
4. Execute the management command rebuild_index and select Y when asked if you want to destroy your index. `docker-compose exec web app/manage.py rebuild_index`

Materialized View SQL follows

```
CREATE OR REPLACE FUNCTION lower_trim_all(text[])
  RETURNS text[] AS
$func$
SELECT ARRAY (
   SELECT regexp_replace(trim(lower(elem)), '\s+', '', 'g')
   FROM   unnest($1) elem
   )
$func$  LANGUAGE sql IMMUTABLE;

DROP MATERIALIZED VIEW IF EXISTS dashboard_userdirectory;

CREATE MATERIALIZED VIEW dashboard_userdirectory
AS
-- load gitcoin profile data
with profiles as (
    select distinct
        b.id profile_id,
        b.user_id,
        b.handle,
        to_timestamp(b.data ->> 'created_at', 'YYYY-MM-DDTHH:MI:SSZ') github_created_at,
        b.email,
        b.preferred_payout_address,
        b.sms_verification,
        a.first_name,
        a.last_name,
        coalesce(b.created_on, a.date_joined) join_date,
        lower_trim_all(b.keywords) keywords,
        b.selected_persona,
        b.activity_level,
        b.reliability,
        b.average_rating,
        b.longest_streak,
        b.earnings_count,
        b.follower_count,
        b.following_count,
        b.num_repeated_relationships,
        b.rank_coder,
        b.rank_funder
    from
        dashboard_profile b
    left join
        auth_user a
    on
        b.user_id = a.id
),


-- load gitcoin action data
actions as (
    select
        du.profile_id,
        du.created_on,
        null bounty_id,
        du.action
    from
        dashboard_useraction du

    union all

    select
        da.profile_id,
        da.created created_on,
        da.bounty_id,
        da.activity_type as action
    from
        dashboard_activity da

    order by profile_id, created_on
),



-- load project data
project_view as (
    select distinct
        *
    from
        dashboard_hackathonproject
),
project_profiles as (
    select
        *
    from
        dashboard_hackathonproject_profiles
),
project_full as (
    select
        v.hackathon_id,
        v.bounty_id,
        v.id project_id,
        v.name project_name,
        v.work_url submission_link,
        p.profile_id,
        pp.handle,
        pp.email,
        pp.preferred_payout_address
    from
        project_view v
    left join
        project_profiles p
    on
        p.hackathonproject_id = v.id
    left join
        profiles pp
    on
        p.profile_id = pp.profile_id
    order by
        project_id
),
project_w_teams as (
    select
        p.hackathon_id,
        p.bounty_id,
        b.organization,
        b.bounty_title,
        b.bounty_url,
        p.project_id,
        p.submission_link,
        string_agg(p.handle, ', ') team_members,
        string_agg(p.email, ', ') team_member_emails,
        string_agg(p.preferred_payout_address, ', ') team_preferred_payout_addresses
    from
        project_full p
    left join (
        select
            db.id bounty_id,
            substring(db.github_url::text, '(?<=https:\/\/github\.com/)([^\/]+)') organization,
            db.title bounty_title,
            db.github_url bounty_url
        from
            dashboard_bounty db
    ) b
    on
        p.bounty_id = b.bounty_id
    group by
        p.hackathon_id,
        p.bounty_id,
        b.organization,
        b.bounty_title,
        b.bounty_url,
        p.project_id,
        p.submission_link
),
additional_projects as (
    select distinct
        organization,
        bounty_title,
        bounty_url,
        submission_link,
        split_part(team_members, ', ', 1) handle_1,
        split_part(team_member_emails, ', ', 1) email_1,
        split_part(team_preferred_payout_addresses, ', ', 1) preferred_payout_address_1,
        split_part(team_members, ', ', 2) handle_2,
        split_part(team_member_emails, ', ', 2) email_2,
        split_part(team_preferred_payout_addresses, ', ', 2) preferred_payout_address_2,
        split_part(team_members, ', ', 3) handle_3,
        split_part(team_member_emails, ', ', 3) email_3,
        split_part(team_preferred_payout_addresses, ', ', 3) preferred_payout_address_3,
        split_part(team_members, ', ', 4) handle_4,
        split_part(team_member_emails, ', ', 4) email_4,
        split_part(team_preferred_payout_addresses, ', ', 4) preferred_payout_address_4,
        split_part(team_members, ', ', 5) handle_5,
        split_part(team_member_emails, ', ', 5) email_5,
        split_part(team_preferred_payout_addresses, ', ', 5) preferred_payout_address_5
    from
        project_w_teams
),



-- load grants data
grants_full as (
    select
        c.created_on contribution_created,
        date(c.created_on) contribution_created_date,
        c.id contribution_id,
        c.subscription_id,
        s.contributor_profile_id,
        s.contributor_address,
        s.amount_per_period,
        s.token_symbol,
        s.frequency,
        s.frequency_unit,
        s.real_period_seconds,
        s.last_contribution_date,
        s.next_contribution_date,
        s.amount_per_period_usdt,
        c.success,
        s.active,
        s.error,
        c.tx_id,
        s.cancel_tx_id,
        g.created_on grant_created_on,
        g.id grant_id,
        g.title,
        g.grant_type_id,
        g.admin_profile_id,
        g.amount_received,
        g.monthly_amount_subscribed
    from
        grants_contribution c
    left join
        grants_subscription s
    on
        c.subscription_id = s.id
    left join
        grants_grant g
    on
        s.grant_id = g.id
    where
        c.success = True
        and
            s.is_postive_vote = True
),



-- load kudos data
kudos_full as (
    select distinct
        a.created_on,
        a.kudos_token_cloned_from_id kudos_id,
        b.name kudos_name,
        b.description,
        a.sender_profile_id,
        a.from_username sender_username,
        a.recipient_profile_id receiver_profile_id,
        split_part(a.username, '@', 2) receiver_username,
        a.txid sender_txid,
        a.receive_txid receiver_txid,
        a.tx_status send_tx_status,
        a.receive_tx_status,
        case
            when a.txid is null or a.txid = '' and a.tx_status in ('pending', 'dropped', 'error', 'na') then 0
            else 1
        end successful_send,
        case
            when a.receive_txid is null or a.receive_txid = '' and a.receive_tx_status in ('pending', 'dropped', 'error', 'na') then 0
            else 1
        end successful_receive,
        case when (a.metadata::json -> 'coupon_redemption')::text = 'true' then 'coupon' else 'organic' end txn_type,
        b.tags,
        b.rarity,
        b.price_finney / 1000::numeric price_ether
    from
        kudos_kudostransfer a
    left join
        kudos_token b
    on
        a.kudos_token_cloned_from_id = b.id
    where
        a.network = 'mainnet'
),



---
---
---



-- detect personas
grouped_actions as (
    select
        a.profile_id,
        a.action,
        count(1) _count
    from
        actions a
    where
        a.action not in ('Login', 'Logout', 'Visit', 'joined')
    group by
        a.profile_id,
        a.action
    order by
        a.profile_id,
        count(1) desc
),
ranked_actions as (
    select
        a.*,
        rank() over (partition by a.profile_id order by a._count desc) _rank
    from
        grouped_actions a
),
funder_actions as (
    select
        *
    from (
        values  -- dominant bounty funder actions based on 4823 (frankchen07)
            ('new_bounty', 'funder'),
            ('work_done', 'funder'),
            ('bounty_changed', 'funder'),
            ('extend_expiration', 'funder'),
            ('increased_bounty', 'funder'),
            ('increase_payout','funder'),
            ('bounty_removed_by_funder', 'funder'),
            ('killed_bounty', 'funder')
        ) as f (funder_action, manual_persona)
),



---
---
---



hackathon_general_metrics as (
    select distinct
        registrant_id profile_id,
        count(distinct hackathon_id) num_hacks_joined,
        array_agg(hackathon_id::text) which_hacks_joined
    from
        dashboard_hackathonregistration
    group by
        registrant_id
),



-- hackathon specific metrics
hackathon_bounties as (
    select
        db.web3_created,
        db.id bounty_id,
        db.event_id,
        db.title,
        db.bounty_type,
        db.github_url bounty_github_url,
        substring(db.github_url::text, '(?<=https:\/\/github\.com/)([^\/]+)') organization,
        db.idx_status,
        db.value_in_usdt
    from
        dashboard_bounty db
    where
        db.current_bounty = True
        and
            db.network = 'mainnet'
        and
            db.event_id not in (0, 1)
        and
            db.idx_status not in ('cancelled')
),
-- load bounty fulfillment data
hackathon_bounties_f as (
    select
        a.created_on,
        a.bounty_id,
        a.fulfiller_metadata::json -> 'data' -> 'payload' ->> 'description' bounty_github_url,
        a.fulfiller_github_url,
        a.profile_id fulfiller_profile_id
    from
        dashboard_bountyfulfillment a
    inner join (
        select distinct bounty_id from hackathon_bounties  -- pull only fulfillments for a specific hack
    ) b
    on
        a.bounty_id = b.bounty_id
),
hackathon_result_raw as (
    select distinct
        b.event_id,
        coalesce(b.bounty_id, f.bounty_id) bounty_id,
        b.organization,
        b.title bounty_title,
        b.bounty_github_url bounty_url,
        b.bounty_type,
        b.value_in_usdt,
        z.issue_message work_plan,
        f.fulfiller_github_url submission_link,
        coalesce(z.profile_id, f.fulfiller_profile_id) interest_profile_id,  -- if stopped work, use fulfiller_profile_id
        pp.handle interest_handle,
        f.fulfiller_profile_id submitter_profile_id,
        p.handle submitter_handle,
        'https://gitcoin.co/profile/' || p.handle submitter_profile_url,
        p.email submitter_email,
        p.preferred_payout_address submitter_preferred_payout_address,
        case when z.profile_id is not null then 1 else 0 end started_boolean,
        case when f.fulfiller_profile_id is not null then 1 else 0 end submitted_boolean
    from
        hackathon_bounties b
    left join
        dashboard_bounty_interested i
    on
        b.bounty_id = i.bounty_id
    left join
        dashboard_interest z
    on
        i.interest_id = z.id
    full outer join
        hackathon_bounties_f f
    on
        b.bounty_id = f.bounty_id and z.profile_id = f.fulfiller_profile_id  -- coalesce above for full outer join
    left join
        profiles p
    on
        f.fulfiller_profile_id = p.profile_id
    left join
        profiles pp
    on
        z.profile_id = pp.profile_id
    where
        (z.profile_id is not null or f.fulfiller_profile_id is not null)
),
hackathon_result as (
    select
        r.bounty_id,
        coalesce(r.organization, bb.organization) organization,
        coalesce(r.bounty_title, bb.bounty_title) bounty_title,
        coalesce(r.bounty_url, bb.bounty_url) bounty_url,
        r.bounty_type,
        r.value_in_usdt,
        r.work_plan,
        r.submission_link,
        r.interest_profile_id,
        r.interest_handle,
        r.submitter_profile_id,
        r.submitter_handle,
        r.submitter_profile_url,
        r.submitter_email,
        r.submitter_preferred_payout_address,
        case when r.submitted_boolean = 1 and r.started_boolean = 0 then 1 else r.started_boolean end started_boolean,  -- pre-fill start works
        r.submitted_boolean
    from
        hackathon_result_raw r
    left join (  -- re-fill empty organization, bounty titles, and bounty_github_urls // (why didn't this work after full outer join?)
        select distinct b.bounty_id, b.organization, b.title bounty_title, b.bounty_github_url bounty_url from hackathon_bounties b
    ) bb
    on
        r.bounty_id = bb.bounty_id
),
hackathon_submit_final as (
    select distinct
        a.organization,
        a.bounty_title,
        a.bounty_url,
        a.started_boolean,
        a.submitted_boolean,
        a.work_plan,
        a.submission_link,
        a.submitter_profile_id,
        a.submitter_handle,
        a.submitter_profile_url,
        a.submitter_email,
        a.submitter_preferred_payout_address,
        b.handle_2,
        b.email_2,
        b.preferred_payout_address_2,
        b.handle_3,
        b.email_3,
        b.preferred_payout_address_3,
        b.handle_4,
        b.email_4,
        b.preferred_payout_address_4,
        b.handle_5,
        b.email_5,
        b.preferred_payout_address_5
    from
        hackathon_result a
    left join
        additional_projects b
    on
        a.organization = b.organization
        and
            a.bounty_title = b.bounty_title
        and
            a.bounty_url = b.bounty_url
        and
            a.submission_link = b.submission_link
        and
            a.submitter_handle = b.handle_1
    order by
        a.bounty_url
),



hackathon_bounties_started_raw as (
    select
        interest_profile_id profile_id,
        bounty_id,
        organization,
        count(1) _count
    from
        hackathon_result
    where
        started_boolean = 1
    group by
        interest_profile_id,
        bounty_id,
        organization
),
hackathon_bounties_started as (
    select
        profile_id,
        sum(_count) hack_work_starts
    from
        hackathon_bounties_started_raw
    where
        profile_id is not null
    group by
        profile_id
),
hackathon_bounties_started_orgs as (
    select
        profile_id,
        array_agg(distinct organization) hack_work_start_orgs
    from
        hackathon_bounties_started_raw
    where
        profile_id is not null
    group by
        profile_id
),



hackathon_bounties_started_raw_type as (
    select
        interest_profile_id profile_id,
        bounty_type,
        count(1) _count
    from
        hackathon_result
    where
        started_boolean = 1
    group by
        interest_profile_id,
        bounty_type
),
hackathon_bounties_started_type as (
    select
        profile_id,
        max(case when bounty_type = 'Feature' then _count else 0 end) hack_started_feature,
        max(case when bounty_type = 'Code Review' then _count else 0 end) hack_started_code_review,
        max(case when bounty_type = 'Security' then _count else 0 end) hack_started_security,
        max(case when bounty_type = 'Design' then _count else 0 end) hack_started_design,
        max(case when bounty_type = 'Documentation' then _count else 0 end) hack_started_documentation,
        max(case when bounty_type = 'Bug' then _count else 0 end) hack_started_bug,
        max(case when bounty_type = 'Other' then _count else 0 end) hack_started_other,
        max(case when bounty_type = 'Improvement' then _count else 0 end) hack_started_improvement
    from
        hackathon_bounties_started_raw_type
    group by
        profile_id
),



hackathon_bounties_submitted as (
    select
        submitter_profile_id profile_id,
        sum(submitted_boolean) hack_work_submits
    from
        hackathon_submit_final
    where
        submitted_boolean = 1
        and
            submitter_profile_id is not null
    group by
        submitter_profile_id
),
hackathon_bounties_submitted_orgs as (
    select
        submitter_profile_id profile_id,
        array_agg(distinct organization) hack_work_submit_orgs
    from
        hackathon_submit_final
    where
        submitted_boolean = 1
        and
            submitter_profile_id is not null
    group by
        submitter_profile_id
),



-- non-hackathon specific metrics
bounties as (
    select
        db.web3_created,
        db.id bounty_id,
        db.event_id,
        db.title,
        db.bounty_type,
        db.github_url bounty_github_url,
        substring(db.github_url::text, '(?<=https:\/\/github\.com/)([^\/]+)') organization,
        db.idx_status,
        db.value_in_usdt
    from
        dashboard_bounty db
    where
        db.current_bounty = True
        and
            db.network = 'mainnet'
        and
            db.idx_status not in ('cancelled')
        and
            db.event_id is null
),
-- load bounty fulfillment data
bounties_f as (
    select
        a.created_on,
        a.bounty_id,
        a.fulfiller_metadata::json -> 'data' -> 'payload' ->> 'description' bounty_github_url,
        a.fulfiller_github_url,
        a.profile_id fulfiller_profile_id
    from
        dashboard_bountyfulfillment a
    inner join (
        select distinct bounty_id from bounties  -- pull only fulfillments for a specific hack
    ) b
    on
        a.bounty_id = b.bounty_id
),
result_raw as (
    select distinct
        b.event_id,
        coalesce(b.bounty_id, f.bounty_id) bounty_id,
        b.organization,
        b.title bounty_title,
        b.bounty_github_url bounty_url,
        b.bounty_type,
        b.value_in_usdt,
        z.issue_message work_plan,
        f.fulfiller_github_url submission_link,
        coalesce(z.profile_id, f.fulfiller_profile_id) interest_profile_id,  -- if stopped work, use fulfiller_profile_id
        pp.handle interest_handle,
        f.fulfiller_profile_id submitter_profile_id,
        p.handle submitter_handle,
        'https://gitcoin.co/profile/' || p.handle submitter_profile_url,
        p.email submitter_email,
        p.preferred_payout_address submitter_preferred_payout_address,
        case when z.profile_id is not null then 1 else 0 end started_boolean,
        case when f.fulfiller_profile_id is not null then 1 else 0 end submitted_boolean
    from
        bounties b
    left join
        dashboard_bounty_interested i
    on
        b.bounty_id = i.bounty_id
    left join
        dashboard_interest z
    on
        i.interest_id = z.id
    full outer join
        bounties_f f
    on
        b.bounty_id = f.bounty_id and z.profile_id = f.fulfiller_profile_id  -- coalesce above for full outer join
    left join
        profiles p
    on
        f.fulfiller_profile_id = p.profile_id
    left join
        profiles pp
    on
        z.profile_id = pp.profile_id
    where
        (z.profile_id is not null or f.fulfiller_profile_id is not null)
),
result as (
    select
        r.event_id,
        r.bounty_id,
        coalesce(r.organization, bb.organization) organization,
        coalesce(r.bounty_title, bb.bounty_title) bounty_title,
        coalesce(r.bounty_url, bb.bounty_url) bounty_url,
        r.bounty_type,
        r.value_in_usdt,
        r.work_plan,
        r.submission_link,
        r.interest_profile_id,
        r.interest_handle,
        r.submitter_profile_id,
        r.submitter_handle,
        r.submitter_profile_url,
        r.submitter_email,
        r.submitter_preferred_payout_address,
        case when r.submitted_boolean = 1 and r.started_boolean = 0 then 1 else r.started_boolean end started_boolean,  -- pre-fill start works
        r.submitted_boolean
    from
        result_raw r
    left join (  -- re-fill empty organization, bounty titles, and bounty_github_urls // (why didn't this work after full outer join?)
        select distinct b.bounty_id, b.organization, b.title bounty_title, b.bounty_github_url bounty_url from bounties b
    ) bb
    on
        r.bounty_id = bb.bounty_id
),
submit_final as (
    select distinct
        a.organization,
        a.bounty_title,
        a.bounty_url,
        a.bounty_type,
        a.started_boolean,
        a.submitted_boolean,
        a.work_plan,
        a.submission_link,
        a.submitter_profile_id,
        a.submitter_handle,
        a.submitter_profile_url,
        a.submitter_email,
        a.submitter_preferred_payout_address,
        b.handle_2,
        b.email_2,
        b.preferred_payout_address_2,
        b.handle_3,
        b.email_3,
        b.preferred_payout_address_3,
        b.handle_4,
        b.email_4,
        b.preferred_payout_address_4,
        b.handle_5,
        b.email_5,
        b.preferred_payout_address_5
    from
        result a
    left join
        additional_projects b
    on
        a.organization = b.organization
        and
            a.bounty_title = b.bounty_title
        and
            a.bounty_url = b.bounty_url
        and
            a.submission_link = b.submission_link
        and
            a.submitter_handle = b.handle_1
    order by
        a.bounty_url
),



bounties_started_raw as (
    select
        interest_profile_id profile_id,
        bounty_id,
        organization,
        sum(value_in_usdt) _value,
        count(1) _count
    from
        result
    where
        started_boolean = 1
    group by
        interest_profile_id,
        bounty_id,
        organization
),
bounties_started as (
    select
        profile_id,
        sum(_count) bounty_work_starts
    from
        bounties_started_raw
    where
        profile_id is not null
    group by
        profile_id
),
bounties_started_orgs as (
    select
        profile_id,
        array_agg(distinct organization) bounty_work_start_orgs
    from
        bounties_started_raw
    where
        profile_id is not null
    group by
        profile_id
),
bounties_earned as (
    select
        profile_id,
        sum(_value) bounty_earnings
    from
        bounties_started_raw
    where
        profile_id is not null
    group by
        profile_id
),



bounties_started_type_raw as (
    select
        interest_profile_id profile_id,
        bounty_type,
        count(1) _count
    from
        result
    where
        started_boolean = 1
    group by
        interest_profile_id,
        bounty_type
),
bounties_started_type as (
    select
        profile_id,
        max(case when bounty_type = 'Feature' then _count else 0 end) started_feature,
        max(case when bounty_type = 'Code Review' then _count else 0 end) started_code_review,
        max(case when bounty_type = 'Security' then _count else 0 end) started_security,
        max(case when bounty_type = 'Design' then _count else 0 end) started_design,
        max(case when bounty_type = 'Documentation' then _count else 0 end) started_documentation,
        max(case when bounty_type = 'Bug' then _count else 0 end) started_bug,
        max(case when bounty_type = 'Other' then _count else 0 end) started_other,
        max(case when bounty_type = 'Improvement' then _count else 0 end) started_improvement
    from
        bounties_started_type_raw
    group by
        profile_id
),
bounties_submitted_type_raw as (
    select
        submitter_profile_id profile_id,
        bounty_type,
        sum(submitted_boolean) bounty_work_submits
    from
        submit_final
    where
        submitted_boolean = 1
        and
            submitter_profile_id is not null
    group by
        submitter_profile_id,
        bounty_type
),
bounties_submitted_type as (
    select
        profile_id,
        max(case when bounty_type = 'Feature' then bounty_work_submits else 0 end) submitted_feature,
        max(case when bounty_type = 'Code Review' then bounty_work_submits else 0 end) submitted_code_review,
        max(case when bounty_type = 'Security' then bounty_work_submits else 0 end) submitted_security,
        max(case when bounty_type = 'Design' then bounty_work_submits else 0 end) submitted_design,
        max(case when bounty_type = 'Documentation' then bounty_work_submits else 0 end) submitted_documentation,
        max(case when bounty_type = 'Bug' then bounty_work_submits else 0 end) submitted_bug,
        max(case when bounty_type = 'Other' then bounty_work_submits else 0 end) submitted_other,
        max(case when bounty_type = 'Improvement' then bounty_work_submits else 0 end) submitted_improvement
    from
        bounties_submitted_type_raw
    group by
        profile_id
),



bounties_submitted as (
    select
        submitter_profile_id profile_id,
        sum(submitted_boolean) bounty_work_submits
    from
        submit_final
    where
        submitted_boolean = 1
        and
            submitter_profile_id is not null
    group by
        submitter_profile_id
),
bounties_submitted_orgs as (
    select
        submitter_profile_id profile_id,
        array_agg(distinct organization) bounty_work_submit_orgs
    from
        submit_final
    where
        submitted_boolean = 1
        and
            submitter_profile_id is not null
    group by
        submitter_profile_id
),



-- grants metrics
num_grants_opened as (
    select
        admin_profile_id profile_id,
        count(distinct grant_id) grants_opened
    from
        grants_full
    group by
        admin_profile_id
),
num_grants_contributed as (
    select
        contributor_profile_id profile_id,
        count(distinct grant_id) grants_contributed
    from
        grants_full
    group by
        contributor_profile_id
),
num_grant_contributions as (
    select
        contributor_profile_id profile_id,
        count(distinct contribution_id) grant_contributions
    from
        grants_full
    group by
        contributor_profile_id
),
grants_amount_contributed as (
    select
        contributor_profile_id profile_id,
        sum(amount_per_period_usdt) grant_contribution_amount
    from
        grants_full
    group by
        contributor_profile_id
),



-- engagement metrics
last_engagement_actions_raw as (
    select
        a.profile_id,
        a.created_on,
        a.action,
        row_number() over (partition by a.profile_id order by created_on desc) action_rank
    from
        actions a
),
last_engagement_actions as (
    select
        a.profile_id,
        a.created_on last_action_on
    from
        last_engagement_actions_raw a
    where
        a.action_rank = 1
),



points_worth as (
    select
        *
    from (
        values
            ('Visit', 0),
            ('Login', 1),
            ('played_quest', 2),
            ('updated_avatar', 1),
            ('new_grant_contribution', 3),
            ('receive_kudos', 1),
            ('joined', 1),
            ('unknown_event', 0),
            ('beat_quest', 3),
            ('start_work', 3),
            ('bounty_abandonment_warning', 0),
            ('new_bounty', 5),
            ('new_kudos', 3),
            ('work_submitted', 4),
            ('Logout', 0),
            ('new_tip', 2),
            ('worker_applied', 2),
            ('send_tip', 2),
            ('status_update', 1),
            ('stop_work', 0),
            ('work_done', 5),
            ('silent_status_update', 1),
            ('hackathon_registration', 3),
            ('worker_approved', 2),
            ('update_grant', 1),
            ('killed_bounty', 0),
            ('wall_post', 1),
            ('leaderboard_rank', 0),
            ('bounty_abandonment_escalation_to_mods', 0),
            ('receive_tip', 0),
            ('bounty_changed', 0),
            ('extend_expiration', 0),
            ('new_grant', 3),
            ('new_grant_subscription', 3),
            ('bounty_removed_by_funder', 0),
            ('created_kudos', 2),
            ('increased_bounty', 0),
            ('bounty_removed_by_staff', 0),
            ('account_disconnected', 0),
            ('new_crowdfund', 0),
            ('created_quest', 2),
            ('worker_rejected', 0),
            ('mini_clr_payout', 0),
            ('killed_grant_contribution', 0),
            ('hackathon_new_hacker', 3),
            ('consolidated_leaderboard_rank', 0),
            ('bounty_removed_slashed_by_staff', 0),
            ('added_slack_integration', 0),
            ('killed_grant', 0),
            ('flagged_grant', 0),
            ('increase_payout', 0),
            ('negative_contribution', 0),
            ('removed_slack_integration', 0),
            ('consolidated_mini_clr_payout', 0),
            ('bounty_abandonment_final', 0),
            ('worker_paid', 3),
            ('noop', 0)
        ) as f (action, action_worth)
),
engagement_actions_raw1 as (
    select distinct
        a.profile_id,
        a.action,
        count(a.action) action_count
    from
        actions a
    group by
        a.profile_id,
        a.action
),
engagement_actions_raw2 as (
    select distinct
        a.profile_id,
        a.action,
        a.action_count,  -- we can pivot these columns separately
        b.action_worth,  -- we can pivot these columns separately
        a.action_count * b.action_worth action_points  -- we can pivot these columns separately
    from
        engagement_actions_raw1 a
    left join
        points_worth b
    on
        a.action = b.action
),

engagement_actions_raw3 as (
    select distinct
        a.profile_id,
        sum(a.action_count) num_actions,
        sum(a.action_points) action_points,
        sum(a.action_points) / sum(a.action_count)::float avg_points_per_action
    from
        engagement_actions_raw2 a
    group by
        a.profile_id
    order by
        sum(a.action_points) desc
),
engagement_actions as (
    select distinct
        a.profile_id,
        a.num_actions,
        a.action_points,
        a.avg_points_per_action,
        b.last_action_on
    from
        engagement_actions_raw3 a
    left join
        last_engagement_actions b
    on
        a.profile_id = b.profile_id
),



-- kudos metrics
hackathon_kudos as (
    select
        a.receiver_profile_id profile_id,
        sum(a.successful_receive) hack_winner_kudos_received
    from (
        select distinct sender_profile_id, receiver_profile_id, kudos_id, created_on, successful_send, successful_receive from kudos_full where description ilike '%%winner%%'
    ) a
    group by
        a.receiver_profile_id
),
kudos_send_actions as (
    select
        a.sender_profile_id profile_id,
        sum(a.successful_send) kudos_sends
    from (
        select distinct sender_profile_id, receiver_profile_id, kudos_id, created_on, successful_send, successful_receive from kudos_full
    ) a
    group by
        a.sender_profile_id
),
kudos_receive_actions as (
    select
        a.receiver_profile_id profile_id,
        sum(a.successful_receive) kudos_receives
    from (
        select distinct sender_profile_id, receiver_profile_id, kudos_id, created_on, successful_send, successful_receive from kudos_full
    ) a
    group by
        a.receiver_profile_id
),
kudos_actions_nohack as (
    select
        coalesce(a.profile_id, b.profile_id) profile_id,
        case when a.kudos_sends is null then 0 else a.kudos_sends end kudos_sends,
        case when b.kudos_receives is null then 0 else b.kudos_receives end kudos_receives
    from
        kudos_send_actions a
    full outer join
        kudos_receive_actions b
    on
        a.profile_id = b.profile_id
    where
        coalesce(a.profile_id, b.profile_id) is not null
),
kudos_actions as (
    select
        coalesce(a.profile_id, b.profile_id) profile_id,
        a.kudos_sends,
        a.kudos_receives,
        b.hack_winner_kudos_received
    from
        kudos_actions_nohack a
    full outer join
        hackathon_kudos b
    on
        a.profile_id = b.profile_id
    where
        coalesce(a.profile_id, b.profile_id) is not null
),



-- compose the user directory
user_directory as (
    select distinct
        r.profile_id,
        p.join_date,
        p.github_created_at,
        p.first_name,
        p.last_name,
        p.email,
        p.handle,
        p.sms_verification,
        case when coalesce(p.selected_persona, f.manual_persona) = '' then 'hunter' else coalesce(p.selected_persona, f.manual_persona) end persona,
        case when p.rank_coder is null then 0 else p.rank_coder end rank_coder,
        case when p.rank_funder is null then 0 else p.rank_funder end rank_funder,
        case when h.num_hacks_joined is null then 0 else h.num_hacks_joined end num_hacks_joined,
        h.which_hacks_joined,
        case when z.hack_work_starts is null then 0 else z.hack_work_starts end hack_work_starts,
        case when y.hack_work_submits is null then 0 else y.hack_work_submits end hack_work_submits,
        k.hack_work_start_orgs,
        l.hack_work_submit_orgs,
        case when s.bounty_work_starts is null then 0 else s.bounty_work_starts end bounty_work_starts,
        case when u.bounty_work_submits  is null then 0 else u.bounty_work_submits  end bounty_work_submits,
        case when zz.hack_started_feature is null then 0 else zz.hack_started_feature end hack_started_feature,
        case when zz.hack_started_code_review is null then 0 else zz.hack_started_code_review end hack_started_code_review,
        case when zz.hack_started_security is null then 0 else zz.hack_started_security end hack_started_security,
        case when zz.hack_started_design is null then 0 else zz.hack_started_design end hack_started_design,
        case when zz.hack_started_documentation is null then 0 else zz.hack_started_documentation end hack_started_documentation,
        case when zz.hack_started_bug is null then 0 else zz.hack_started_bug end hack_started_bug,
        case when zz.hack_started_other is null then 0 else zz.hack_started_other end hack_started_other,
        case when zz.hack_started_improvement is null then 0 else zz.hack_started_improvement end hack_started_improvement,
        case when ss.started_feature is null then 0 else ss.started_feature end started_feature,
        case when ss.started_code_review is null then 0 else ss.started_code_review end started_code_review,
        case when ss.started_security is null then 0 else ss.started_security end started_security,
        case when ss.started_design is null then 0 else ss.started_design end started_design,
        case when ss.started_documentation is null then 0 else ss.started_documentation end started_documentation,
        case when ss.started_bug is null then 0 else ss.started_bug end started_bug,
        case when ss.started_other is null then 0 else ss.started_other end started_other,
        case when ss.started_improvement is null then 0 else ss.started_improvement end started_improvement,
        case when uu.submitted_feature is null then 0 else uu.submitted_feature end submitted_feature,
        case when uu.submitted_code_review is null then 0 else uu.submitted_code_review end submitted_code_review,
        case when uu.submitted_security is null then 0 else uu.submitted_security end submitted_security,
        case when uu.submitted_design is null then 0 else uu.submitted_design end submitted_design,
        case when uu.submitted_documentation is null then 0 else uu.submitted_documentation end submitted_documentation,
        case when uu.submitted_bug is null then 0 else uu.submitted_bug end submitted_bug,
        case when uu.submitted_other is null then 0 else uu.submitted_other end submitted_other,
        case when uu.submitted_improvement is null then 0 else uu.submitted_improvement end submitted_improvement,
        case when q.bounty_earnings is null then 0 else q.bounty_earnings end bounty_earnings,
        m.bounty_work_start_orgs,
        n.bounty_work_submit_orgs,
        case when v.kudos_sends is null then 0 else v.kudos_sends end kudos_sends,
        case when v.kudos_receives is null then 0 else v.kudos_receives end kudos_receives,
        case when v.hack_winner_kudos_received is null then 0 else v.hack_winner_kudos_received end hack_winner_kudos_received,
        case when g.grants_opened is null then 0 else g.grants_opened end grants_opened,
        case when c.grants_contributed is null then 0 else c.grants_contributed end grant_contributed,
        case when d.grant_contributions is null then 0 else d.grant_contributions end  grant_contributions,
        case when e.grant_contribution_amount is null then 0 else e.grant_contribution_amount end grant_contribution_amount,
        case when j.num_actions is null then 0 else j.num_actions end num_actions,
        case when j.action_points is null then 0 else j.action_points end action_points,
        case when j.avg_points_per_action is null then 0 else j.avg_points_per_action end avg_points_per_action,
        j.last_action_on,
        p.keywords,
        p.activity_level,
        p.reliability,
        case when p.average_rating is null then 0 else p.average_rating end average_rating,
        case when p.longest_streak is null then 0 else p.longest_streak end longest_streak,
        case when p.earnings_count is null then 0 else p.earnings_count end earnings_count,
        case when p.follower_count is null then 0 else p.follower_count end follower_count,
        case when p.following_count is null then 0 else p.following_count end following_count,
        case when p.num_repeated_relationships is null then 0 else p.num_repeated_relationships end num_repeated_relationships,
        case
            when p.sms_verification = true and e.grant_contribution_amount > 1000 then 'verified'
            when u.bounty_work_submits >= 3 or y.hack_work_submits >= 3 or q.bounty_earnings > 1000 then 'verified'
            when j.action_points >= 500 then 'verified'
            when v.hack_winner_kudos_received >= 1 or v.kudos_sends >= 10 or v.kudos_receives >= 20 then 'verified'
            else 'not verified'
        end verification_status
    from
        ranked_actions r
    left join
        funder_actions f
    on
        r.action = f.funder_action
    left join
        profiles p
    on
        r.profile_id = p.profile_id
    left join
        hackathon_general_metrics h
    on
        r.profile_id = h.profile_id
    left join
        hackathon_bounties_started z
    on
        r.profile_id = z.profile_id
    left join
        hackathon_bounties_submitted y
    on
        r.profile_id = y.profile_id
    left join
        hackathon_bounties_started_type zz
    on
        r.profile_id = zz.profile_id
    left join
        hackathon_bounties_started_orgs k
    on
        r.profile_id = k.profile_id
    left join
        hackathon_bounties_submitted_orgs l
    on
        r.profile_id = l.profile_id
    left join
        bounties_started s
    on
        r.profile_id = s.profile_id
    left join
        bounties_submitted u
    on
        r.profile_id = u.profile_id
    left join
        bounties_started_type ss
    on
        r.profile_id = ss.profile_id
    left join
        bounties_submitted_type uu
    on
        r.profile_id = uu.profile_id
    left join
        bounties_earned q
    on
        r.profile_id = q.profile_id
    left join
        bounties_started_orgs m
    on
        r.profile_id = m.profile_id
    left join
        bounties_submitted_orgs n
    on
        r.profile_id = n.profile_id
    left join
        kudos_actions v
    on
        r.profile_id = v.profile_id
    left join
        num_grants_opened g
    on
        r.profile_id = g.profile_id
    left join
        num_grants_contributed c
    on
        r.profile_id = c.profile_id
    left join
        num_grant_contributions d
    on
        r.profile_id = d.profile_id
    left join
        grants_amount_contributed e
    on
        r.profile_id = e.profile_id
    left join
        engagement_actions j
    on
        r.profile_id = j.profile_id
    where
        r._rank = 1
)

SELECT * FROM user_directory;

REFRESH MATERIALIZED VIEW dashboard_userdirectory;
```