class RequestFormWrapper:
    """
    We do magic stuff to wrap original admin form.
    it returns instance that stores original form and request object, and when django admin would like to init the form
    by calling the form class (in usual way for creating instances of any object in python: SomeClass(...init_args)
    then the __call__ function will be invoked (as the get_form method of the admin interface returned instance of this
    wrapper instead of the form class), but the __call__ function will instantiate the form class, but apart from the
    original init params it will pass also request object - and the __call__ function returns the initiated that way
    the form)
    """
    def __init__(self, the_form, request):
        self._the_form = the_form
        self._request = request

    def __call__(self, *args, **kwargs):
        return self._the_form(request=self._request, *args, **kwargs)

    def __getattr__(self, item):
        """
        It is because some admin code wants to get some attributes from the non-initiated form class itself
        (like form.base_fields)
        """
        return getattr(self._the_form, item)


class AdminRequestFormMixIn:
    """
    This mix-in is to be used with admin.ModelAdmin classes. It is to be used when we want to pass request object to the
    form class. It is because the admin.ModelAdmin class does not have access to the request object, but the form class
    does not have access to the admin.ModelAdmin class. So we use this mix-in to pass the request
    """
    def get_form(self, request, obj=None, **kwargs):
        """
        This is the method that is called by django admin to get the form class to be used for the admin page
        """
        form = super().get_form(request, obj, **kwargs)
        return RequestFormWrapper(form, request)
