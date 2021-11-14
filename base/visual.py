from .models import Profile


def get_data(foo):
    p = Profile.objects.all()

    for pf in p:
        if foo(pf):
            print(pf.handle, pf.rating_progress, pf.history)
