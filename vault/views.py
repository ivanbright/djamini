from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import LicenseAccessForm, LicenseForm
from .models import License, LicenseAccess, can_access


class LicenseQuerysetMixin:
    # fetched once per request, then reused
    def get_license(self):
        if not hasattr(self, '_license'):
            self._license = get_object_or_404(License, pk=self.kwargs['pk'])
        return self._license

    def get_object(self, queryset=None):
        return self.get_license()


class AccessRequiredMixin(LoginRequiredMixin, LicenseQuerysetMixin):
    # blocked group? straight to 403
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not can_access(request.user, self.get_license()):
            return HttpResponseForbidden(
                'Your group is blocked from this license.'
            )
        return super().dispatch(request, *args, **kwargs)


class OwnerRequiredMixin(AccessRequiredMixin):
    # only the owner gets to edit it
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.get_license().owner_id != request.user.id:
            raise PermissionDenied('Only the owner can manage this license.')
        return super().dispatch(request, *args, **kwargs)


class LicenseListView(LoginRequiredMixin, ListView):
    model = License
    template_name = 'vault/license_list.html'
    context_object_name = 'licenses'

    def get_queryset(self):
        return [license for license in License.objects.all()
                if can_access(self.request.user, license)]


class LicenseDetailView(AccessRequiredMixin, DetailView):
    template_name = 'vault/license_detail.html'
    context_object_name = 'license'


class LicenseCreateView(LoginRequiredMixin, CreateView):
    model = License
    form_class = LicenseForm
    template_name = 'vault/license_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class LicenseUpdateView(OwnerRequiredMixin, UpdateView):
    form_class = LicenseForm
    template_name = 'vault/license_form.html'
    context_object_name = 'license'


class LicenseDeleteView(OwnerRequiredMixin, DeleteView):
    template_name = 'vault/license_confirm_delete.html'
    context_object_name = 'license'
    success_url = reverse_lazy('vault:license_list')


class LicenseAccessView(OwnerRequiredMixin, View):
    # tick groups to block; everyone else keeps access
    template_name = 'vault/license_access.html'

    def get(self, request, pk):
        license = self.get_license()
        form = LicenseAccessForm(initial={'blocked_groups': license.blocked_groups})
        return render(request, self.template_name, {'license': license, 'form': form})

    def post(self, request, pk):
        license = self.get_license()
        form = LicenseAccessForm(request.POST)
        if form.is_valid():
            license.access_rules.all().delete()
            for group in form.cleaned_data['blocked_groups']:
                LicenseAccess.objects.create(
                    license=license, group=group, is_blocked=True
                )
            messages.success(request, 'Access updated.')
            return redirect('vault:license_detail', pk=license.pk)
        return render(request, self.template_name, {'license': license, 'form': form})
