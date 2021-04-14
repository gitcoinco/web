# Performance Testing

Why does performance matter? 
1. Speed = Trust!
2. If the site is performant (especially on routes that get a lot of traffic, then there are less bottlenecks where the thundering herd can take down the site!  (App Servers first, then DB server)

# Computer Science Refresher

CPU L1/L2 cache is 10x faster than
Memory, which is 10x faster than
disk, which is 10x faster than 
network, which is 10x faster than
a human doing something

# App Tuning

## Preventative Measures

1. Use `ratelimit` to limit the number of times a specific user can hit a route.
2. Horizontal scaling of app servers (less easy to do with DB servers)
3. Use `.cache()` on a query that will take a lot of DB cycles to execute.  

## Proactive Measures

1. Limit the number of DB queries per read
2. Limit the number of in-memory operations that need to be done to serve a request (esp if O(n^2) or above)
3. Leverage DB indices as much as possible
4. Cache data on write (instead of generating it on read)


# Handy Links

- Datadog Traces - https://app.datadoghq.com/apm/traces?end=1616640504005&paused=true&query=env%3Aprod%20service%3Acelery-worker&start=1616640502671&streamTraces=true&topLevelSpansOnly=true
- DataDog App servers - https://app.datadoghq.com/dashboard/hqu-92q-auf/app-servers?from_ts=1611496890412&is_auto=false&live=true&page=0&to_ts=1611583290412
- DataDog App server logs https://app.datadoghq.com/logs?index=%2A&query=

# Tools
- Use `ngxtop` on a server, in order to see which requests it is serving (esp useful if the app server is overloaded)
- Use `select * from pg_stat_activity` on the postgres server to see queries that are running on it (useful if DB is overloaded or locked)
- Python tool you can use to see the exact microseconds:  `import time; print(round(time.time(), 2))` that a call is at 


