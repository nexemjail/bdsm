from __future__ import print_function
from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from list_requests import list_request
from .forms import OrderIdForm, ClientIdForm, LoginForm,\
    RegistrationForm, OrderForm, OrderFormToValidate, ClientForm,\
    ChangePasswordForm, CreateUserForm, BonusForm, DiscountForm, ServiceForm, OfficeForm
from registraton_authorization import login as logging_in
from registraton_authorization import register as register_in_db
from registraton_authorization import insert_order ,\
    return_order as set_order_status_to_returned,\
    set_order_ready, update_client as update_client_in_db,\
    update_user_password, create_user_in_db, create_bonus_in_db,\
    call_function_in_db, call_procedure_in_db

from errors import AccessDeniedError


def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            p1 = form.cleaned_data['password_1']
            p2 = form.cleaned_data['password_2']
            if p1 == p2:
                if update_user_password(request, request.COOKIES['username'], p1):
                    return render(request, 'django_app/index.html', {'message': 'changed!'})
        return render(request, 'django_app/update_pass_form.html', {'form': form, 'message': 'invalid_form'})
    else:
        form = ChangePasswordForm()
        return render(request, 'django_app/update_pass_form.html', {'form' : form})


def get_clients(request):
    try:
        row_names, data = list_request(request, 'get_clients')
    except AccessDeniedError:
        return render(request, 'django_app/client_list.html',
                  {"error": True})
    extra_thing = {'url': 'django_app:update_client', 'text': 'Update client'}
    return render(request, 'django_app/client_list.html',
                  {"headers": row_names, "data": data, "error" : False, 'extra_thing' : extra_thing})


def update_client(request, client_id):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            if update_client_in_db(request, first_name, last_name, client_id):
                resp = HttpResponseRedirect(reverse('django_app:index'))
                resp.write(render(request, 'django_app/index.html', {'message': 'client updated'}))
                return resp
            else:
                resp = HttpResponseRedirect(reverse('django_app:index'))
                resp.write(render(request, 'django_app/index.html', {'message': 'Error while updating'}))
                return resp
        return render(request, 'django_app/client_form.html', {'form': form, 'id': client_id})

    else:
        row_names, record = list_request(request, 'client_info', [int(client_id)])
        form = ClientForm(data={'first_name': record[0][1], 'last_name': record[0][2], 'best_client': record[0][3]})
        return render(request, 'django_app/client_form.html', {'form': form, 'id' : record[0][0]})


def client_info(request, client_id):
    try:
        row_names, data = list_request(request, 'client_info', [int(client_id)])
        is_ready_index = row_names.index('Best client')
        for i, element in enumerate(data):
            data[i] = list(data[i])
            data[i][is_ready_index] = bool(element[is_ready_index])
            extra_thing = {'url': 'django_app:update_client', 'text': 'Update client'}
        return render(request, 'django_app/client_info.html',
                      {"headers": row_names, "data": data, 'extra_thing': extra_thing})
    except AccessDeniedError:
        return render(request, 'django_app/client_info.html',
                      {"error": True})


def get_offices(request):
    try:
        row_names, data = list_request(request, 'get_offices')
        extra_thing = None
        if 'connection' in request.COOKIES and request.COOKIES['connection'] == 'admin':
            extra_thing = {'url': 'django_app:update_office', 'text': 'Update office'}
        return render(request, 'django_app/list_template.html',
                      {"headers": row_names, "data": data, 'extra_thing': extra_thing})
    except AccessDeniedError:
        return render(request, 'django_app/list_template.html',
                      {"error": True})


def update_office(request, office_id):
    if request.method == 'POST':
        form = OfficeForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['location']
            value = form.cleaned_data['description']
            if call_procedure_in_db(request, 'update_office_by_id', [int(office_id), description, value]):
                return render(request, 'django_app/index.html', {'message': 'office updated'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error while updating'})
        return render(request, 'django_app/edit_form_template.html',
                      {'form': form, 'id': office_id,
                       'url_': 'django_app:update_office'})

    else:
        row_names, record = list_request(request, 'get_office_by_id', [int(office_id)])
        form = OfficeForm(data={'location': record[0][1], 'description': record[0][2]})
        return render(request, 'django_app/edit_form_template.html', {'form': form, 'id': office_id,
                                                                      'url_': 'django_app:update_office'})


def index(request):
    return render(request, 'django_app/index.html')


def get_order_info(request, order_id):
    try:
        row_names, data = list_request(request, 'get_order_info', [int(order_id)])
        is_ready_index = row_names.index('Is ready')
        for i, element in enumerate(data):
            data[i] = list(data[i])
            data[i][is_ready_index] = bool(element[is_ready_index])

        return render(request, 'django_app/order_status.html',
                      {"headers": row_names, "data": data})
    except AccessDeniedError:
        return render(request, 'django_app/order_status.html',
                      {"error" : True})


def check_order(request):
    if request.method == 'POST':
        form = OrderIdForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']
            return HttpResponseRedirect(reverse('django_app:order', args=(order_id,)))
    else:
        form = OrderIdForm()
        return render(request, 'django_app/check_order.html', {"form": form})


def client_orders(request, client_id):
    try:
        row_names, data = list_request(request, 'client_orders', [int(client_id)])
        is_ready_index = row_names.index('Is ready')
        for i, element in enumerate(data):
            data[i] = list(data[i])
            data[i][is_ready_index] = bool(element[is_ready_index])

        return render(request, 'django_app/client_orders_list.html',
                      {"headers": row_names, "data": data})
    except AccessDeniedError:
        return render(request, 'django_app/client_orders_list.html',
                      {"error": True})


def check_client_orders(request):
    if request.method == 'POST':
        form = ClientIdForm(request.POST)
        if form.is_valid():
            client_id = form.cleaned_data['client_id']
            return HttpResponseRedirect(reverse('django_app:client_orders', args=(client_id,)))
    else:
        form = ClientIdForm()
        return render(request, 'django_app/check_client_orders.html', {"form": form})


def all_ready_not_returned_orders(request):
    try:
        row_names, data = list_request(request, 'get_ready_not_returned_orders')
        is_ready_index = row_names.index('Is ready')
        for i, element in enumerate(data):
            data[i] = list(data[i])
            data[i][is_ready_index] = bool(element[is_ready_index])
        extra_thing = None
        if 'connection' in request.COOKIES and request.COOKIES['connection'] == 'worker':
            extra_thing = {'url': 'django_app:return_order', 'text': 'Return'}
        return render(request, 'django_app/orders_ready_not_returned_list.html',
                      {"headers": row_names, "data": data, 'extra_thing': extra_thing})
    except AccessDeniedError:
        return render(request, 'django_app/orders_ready_not_returned_list.html',
                      {"error": True})


def client_orders_ready_not_returned(request, client_id):
    try:
        row_names, data = list_request(request, 'ready_not_returned', [int(client_id)])
        is_ready_index = row_names.index('Is ready')
        for i, element in enumerate(data):
            data[i] = list(data[i])
            data[i][is_ready_index] = bool(element[is_ready_index])
        extra_thing = None
        if 'connection' in request.COOKIES and request.COOKIES['connection'] == 'worker':
            extra_thing = {'url': 'django_app:return_order', 'text': 'Return'}
        return render(request, 'django_app/orders_ready_not_returned_list.html',
                      {"headers": row_names, "data": data, 'extra_thing': extra_thing})
    except AccessDeniedError:
        return render(request, 'django_app/orders_ready_not_returned_list.html',
                      {"error": True})


def check_client_orders_ready_not_returned(request):
    if request.method == 'POST':
        form = ClientIdForm(request.POST)
        if form.is_valid():
            client_id = form.cleaned_data['client_id']
            return HttpResponseRedirect(reverse('django_app:ready_not_returned_orders', args=(client_id,)))
    else:
        form = ClientIdForm()
        return render(request, 'django_app/check_orders_ready_not_returned.html', {"form": form})


def check_client_info(request):
    if request.method == 'POST':
        form = ClientIdForm(request.POST)
        if form.is_valid():
            client_id = form.cleaned_data['client_id']
            return HttpResponseRedirect(reverse('django_app:client_info', args=(client_id,)))
    else:
        form = ClientIdForm()
        return render(request, 'django_app/check_client_info.html', {"form": form})


def logout(request):
    resp = HttpResponseRedirect(reverse('django_app:index'))
    resp.delete_cookie('username')
    resp.delete_cookie('connection')
    resp.delete_cookie('client_id')
    # resp.write(render(request, 'django_app/index.html'))
    return resp


def login(request):
    print(request.COOKIES)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']

            login_successful, cookie_values = logging_in(username, password)
            if login_successful:
                resp = HttpResponseRedirect(reverse('django_app:index'))
                resp.set_cookie('username', cookie_values['username'])
                resp.set_cookie('connection', cookie_values['connection'])
                resp.set_cookie('client_id', cookie_values['client_id'])
                resp.write(render(request, 'django_app/index.html', ))
                return resp
            else:
                return render(request, 'django_app/login_form.html',
                      {"form": form, "message": 'Login failed'})
        else:
            return render(request, 'django_app/login_form.html',
                            {"form": form, "message": 'Invalid form!'})
    else:
        form = LoginForm()
        return render(request, 'django_app/login_form.html', {"form": form, "message": None})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            client_id = form.cleaned_data['client_id']
            if register_in_db(username, password, int(client_id)):
                resp = HttpResponseRedirect(reverse('django_app:index'))
                resp.write(render(request, 'django_app/index.html'))
                return resp
        else:
            return render(request, 'django_app/registration_form.html',
                          {"form": form, 'message': 'Invalid input'})
    else:
        form = RegistrationForm()
        return render(request, 'django_app/registration_form.html', {"form": form, 'message': None})


def update_service(request, service_id):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            price = float(form.cleaned_data['price'])
            if call_procedure_in_db(request, 'update_service_by_id', [int(service_id), name, price]):
                return render(request, 'django_app/index.html', {'message': 'service updated'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error while updating'})
        return render(request, 'django_app/edit_form_template.html',
                      {'form': form, 'id': service_id,
                       'url_': 'django_app:update_service'})

    else:
        row_names, record = list_request(request, 'get_service_by_id', [int(service_id)])
        form = ServiceForm(data={'name': record[0][1], 'price': record[0][2]})
        return render(request, 'django_app/edit_form_template.html', {'form': form, 'id': service_id,
                                                                      'url_': 'django_app:update_service'})


def services(request):
    row_names, data = list_request(request, 'get_service_types')
    # is_ready_index = row_names.index('Best clienxt')
    # for i, element in enumerate(data):
    #     data[i] = list(data[i])
    #     data[i][is_ready_index] = bool(element[is_ready_index])
    extra_thing = None
    if request.COOKIES.has_key('connection') and request.COOKIES['connection'] == 'admin':
        extra_thing = {'url': 'django_app:update_service', 'text': 'Edit service'}
    return render(request, 'django_app/service_types_list.html',
                  {"headers": row_names, "data": data, "extra_thing": extra_thing})


def order(request):
    if request.method == 'POST':
        #form = OrderForm(request.POST)
        #form = request.POST['form']
        print(request.POST)
        form = OrderFormToValidate(request.POST)
        if form.is_valid():
            client_id = int(form.cleaned_data['client_id'])
            service_type_id = int(form.cleaned_data['service_type_id'])
            service_bonus_id = form.cleaned_data['service_bonus_id']
            if service_bonus_id is not None:
                service_bonus_id = int(service_bonus_id)

            amount = int(form.cleaned_data['amount'])
            office_id = int(form.cleaned_data['office_id'])
            discount_type_id = form.cleaned_data['discount_type_id']
            if discount_type_id is not None:
                discount_type_id = int(discount_type_id)
            worker_login = request.COOKIES['username']
            print(worker_login)
            if insert_order(request,client_id,service_type_id, service_bonus_id,
                            office_id,worker_login, amount, discount_type_id):
                # resp = HttpResponseRedirect(reverse('django_app:index'))
                resp = render(request, 'django_app/index.html', {"message": 'Order added successfully'})
                return resp
        form = OrderForm(request=request)
        return render(request, 'django_app/order_form.html',
                        {"form": form, 'message': 'Invalid input'})
    else:
        form = OrderForm(request=request)
        return render(request, 'django_app/order_form.html', {"form": form, 'message': None})


# def edit_order(request, order_id):
#     # if request.method == 'POST':
#     # form = OrderForm(request=request)
#     order_id = int(order_id)
#     print(order_id)
#     return render(request, 'django_app/index.html',   {'message': 'got ' + str(order_id)})


def all_orders(request):
    row_names, data = list_request(request, 'get_orders')
    return render(request, 'django_app/orders_list.html', {'data': data, 'headers': row_names})


def set_order_ready_status(request, order_id):
    order_id = int(order_id)
    if set_order_ready(request, order_id):
        return HttpResponseRedirect(reverse('django_app:all_orders'),)
    return render(request, 'django_app/index.html', {"message": 'Error while setting status to READY'})


def return_order(request, order_id):
    order_id = int(order_id)
    if set_order_status_to_returned(request, order_id):
        return render(request, 'django_app/index.html', {'message': "Order returned!"})
    else:
        return render(request, 'django_app/index.html', {'message':
                                                             "error while setting status to order"})


def create_user(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            if create_user_in_db(request, login, password, role):
                return render(request,'django_app/index.html', {'message': 'User created!'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error occured!'})
        return render(request, 'django_app/create_user_form.html', {'form': form})
    else:
        form = CreateUserForm()
        return render(request, 'django_app/create_user_form.html', {'form': form})


def create_bonus(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            type = form.cleaned_data['type']
            value = form.cleaned_data['value']
            if create_bonus_in_db(request, type, value):
                return render(request, 'django_app/index.html', {'message': 'bonus created'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error while creating a bonus'})

        else:
            return render(request, 'django_app/form_template.html', {'form': form, 'message': 'form is invalid'})
    else:
        form = ServiceForm()
        return render(request, 'django_app/bonus_form.html', {'form': form})


def get_bonuses(request):
    row_names, data = list_request(request, 'get_bonuses')
    extra_thing = None
    if 'connection' in request.COOKIES and request.COOKIES['connection'] == 'admin':
        extra_thing = {'url': 'django_app:update_bonus', 'text': 'Update bonus'}
    return render(request, 'django_app/list_template.html', {'data': data, 'headers': row_names,
                                                             'extra_thing': extra_thing})


def update_bonus(request, bonus_id):
    if request.method == 'POST':
        form = BonusForm(request.POST)
        if form.is_valid():
            type = form.cleaned_data['type']
            value = float(form.cleaned_data['value'])
            if call_procedure_in_db(request, 'update_bonus_by_id', [int(bonus_id), type, value]):
                return render(request, 'django_app/index.html', {'message': 'bonus updated'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error while updating'})
        return render(request, 'django_app/edit_form_template.html',
                      {'form': form, 'id': bonus_id,
                       'url_': 'django_app:update_bonus'})

    else:
        row_names, record = list_request(request, 'get_bonus_by_id', [int(bonus_id)])
        form = BonusForm(data={'type': record[0][1], 'value': record[0][2]})
        return render(request, 'django_app/edit_form_template.html', {'form': form, 'id': bonus_id,
                                                                      'url_': 'django_app:update_bonus'})






def create_discount(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            value = form.cleaned_data['value']
            if call_procedure_in_db(request, 'insert_discount_type', [description, value]):
                return render(request, 'django_app/index.html', {'message': 'discount created'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error while creating a discount'})

        else:
            return render(request, 'django_app/form_template.html', {'form': form,
                                                                          'url_': 'django_app:create_discount',
                                                                          'message': 'form is invalid'})
    else:
        form = DiscountForm()
        return render(request, 'django_app/form_template.html', {'form': form,'url_': 'django_app:create_discount'})


def get_discounts(request):
    row_names, data = list_request(request, 'get_discount_types')
    extra_thing = None
    if 'connection' in request.COOKIES and request.COOKIES['connection'] == 'admin':
        extra_thing = {'url': 'django_app:update_discount', 'text': 'Update discount'}
    return render(request, 'django_app/list_template.html', {'data': data, 'headers': row_names,
                                                             'extra_thing': extra_thing})


def update_discount(request, discount_id):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            value = float(form.cleaned_data['value'])
            if call_procedure_in_db(request, 'update_discount_by_id', [int(discount_id), description, value]):
                return render(request, 'django_app/index.html', {'message': 'discount updated'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error while updating'})
        return render(request, 'django_app/edit_form_template.html',
                      {'form': form, 'id': discount_id,
                       'url_': 'django_app:update_discount'})

    else:
        row_names, record = list_request(request, 'get_discount_by_id', [int(discount_id)])
        form = DiscountForm(data={'description': record[0][1], 'value': record[0][2]})
        return render(request, 'django_app/edit_form_template.html', {'form': form, 'id': discount_id,
                                                                      'url_': 'django_app:update_discount'})


def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            if call_procedure_in_db(request, 'insert_service_type', [name, price]):
                return render(request, 'django_app/index.html', {'message': 'service created'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error while creating a service'})

        else:
            return render(request, 'django_app/form_template.html', {'form': form,
                                                                          'url_': 'django_app:create_service',
                                                                          'message': 'form is invalid'})
    else:
        form = ServiceForm()
        return render(request, 'django_app/form_template.html',
                      {'form': form,'url_': 'django_app:create_service'})


def create_office(request):
    if request.method == 'POST':
        form = OfficeForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']
            description = form.cleaned_data['description']
            if call_procedure_in_db(request, 'insert_office', [location, description]):
                return render(request, 'django_app/index.html', {'message': 'service created'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error while creating a service'})

        else:
            return render(request, 'django_app/form_template.html', {'form': form,
                                                                          'url_': 'django_app:create_office',
                                                                          'message': 'form is invalid'})
    else:
        form = OfficeForm()
        return render(request, 'django_app/form_template.html',
                          {'form': form,'url_': 'django_app:create_office'})


def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            f_name = form.cleaned_data['first_name']
            l_name = form.cleaned_data['last_name']
            if call_procedure_in_db(request, 'insert_client', [f_name, l_name, 0]):
                return render(request, 'django_app/index.html', {'message': 'client created'})
            else:
                return render(request, 'django_app/index.html', {'message': 'Error while creating a client'})

        else:
            return render(request, 'django_app/form_template.html', {'form': form,
                                                                          'url_': 'django_app:create_client',
                                                                          'message': 'form is invalid'})
    else:
        form = ClientForm()
        return render(request, 'django_app/form_template.html',
                          {'form': form, 'url_': 'django_app:create_client'})