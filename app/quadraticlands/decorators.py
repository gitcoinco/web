from django.shortcuts import redirect


def is_staff_or_ql_tester(view_func):
    def wrap(request, *args, **kwargs):
        try :
            profile = request.user.profile

            is_allowed = profile.user.groups.filter(name='QL_TESTER').cache().exists()

            if request.user.is_staff or is_allowed:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('/')
        except:
            return redirect('/')
    
    wrap.__doc__ = view_func.__doc__
    wrap.__name__ = view_func.__name__
    return wrap
