# Advanced Usage

## Performance and Profiling

You can profile functions locally by enabling [Django Silk](https://github.com/jazzband/django-silk) by setting the environment variable: `ENABLE_SILK` to `on` in your `.env` file.  If your local environment is already running, you will need to restart the web application via: `docker-compose restart web`

### Profiling a method

Once enabled, you may use `silk` by decorating methods with `@silk_profile`. For example:

```python
from silk.profiling.profiler import silk_profile


@silk_profile(name='View About')
def about(request):
    context = {
        'active': 'about',
        'title': 'About',
    }
    return TemplateResponse(request, 'about.html', context)
```

### Viewing Profiling Results

You may view the profiling results by visiting: [http://localhost:8000/silk](http://localhost:8000/silk)

### Additional Help

- [Silk Documentation](http://silk.readthedocs.io/en/latest/index.html)
- [Silk Github](https://github.com/jazzband/django-silk)
- [Gitcoin Environment Variable Documentation](https://docs.gitcoin.co/mk_envvars/)
