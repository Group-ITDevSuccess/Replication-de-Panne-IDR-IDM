from django.shortcuts import render

from apps.form import SearchForm, MachineForm


# Create your views here.
def index(request):
    companies = []
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            companies = form.cleaned_data.get('company')
        # print(companies, request.POST)

    else:
        form = SearchForm()
    context = {
        'form': form,
        'form_add_machine': MachineForm(),
        'companies': companies
    }
    return render(request, 'apps/index.html', context)
