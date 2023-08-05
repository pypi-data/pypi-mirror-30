# -*- coding: utf-8 -*-
import importlib

from health_check.settings import settings

__all__ = ['Provider', 'Resource']


class Provider:
    """
    Wrapper that handles a check provider, giving easy access to them with dynamic imports from string.
    """

    def __init__(self, name, provider, args, kwargs):
        """
        Create a provider.

        :param name: Provider name.
        :param provider: Provider function or string.
        :param args: Provider args.
        :param kwargs: Provider kwargs.
        """
        self.name = name

        if isinstance(provider, str):
            provider_module, provider_func = provider.rsplit('.', 1)
            module = importlib.import_module(provider_module)
            self.provider = getattr(module, provider_func, None)
            if self.provider is None:
                raise ValueError('Provider not found: %s' % (provider,))
        else:
            self.provider = provider

        self.args = args or ()
        self.kwargs = kwargs or {}

    def __call__(self, *args, **kwargs):
        """
        Return provider results.

        :param args: Provider args.
        :param kwargs: Provider kwargs
        :return: Results after evaluates provider.
        """
        if not args:
            args = self.args  # pragma: no cover

        if not kwargs:
            kwargs = self.kwargs  # pragma: no cover

        return self.provider(*args, **kwargs)


class Resource:
    """
    Wrapper that handles a whole resource with its providers.
    """

    def __init__(self, name):
        """
        Create a resource and all its providers.

        :param name: Resource name
        """
        self.name = name
        try:
            self.providers = {name: Provider(name=name, provider=provider, args=args, kwargs=kwargs)
                              for name, provider, args, kwargs in settings.providers[self.name]}
        except KeyError:
            raise ValueError("Resource doesn't exists: %s" % (self.name,))

    def __call__(self, providers=None, *args, **kwargs):
        """
        Return results from specific providers of this resource. If no providers are specified, return results from
        all defined providers in the resource.

        :param providers: Specific providers to check.
        :return: Results after evaluate each provider.
        """
        if providers:
            try:
                result = {provider: self.providers[provider]() for provider in providers}
            except KeyError as e:
                raise ValueError("Provider %s does not exists in resource %s", e, self.name)
        else:
            result = {name: provider() for name, provider in self.providers.items()}

        return result
