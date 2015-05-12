__author__ = 'had'

from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django_tables2 import RequestConfig
from ticket.forms import TicketForm, ResponseForm, StatusForm
from ticket.models import Tickets, UserProfile, Follow
from ticket.views.auth import home
from ticket.tables import TicketsTables
from django.contrib import messages
from django.utils.translation import ugettext as _
from ticket.tasks import send_new_ticket_all_staff, handle_uploaded_file
from djangoticket.settings import USE_MAIL


@login_required(login_url='login/')
def add_ticket(request):

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, user=request.user)
        # return redirect('/')

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.create_by = request.user
            ticket.created = datetime.now()

            try:
                entity = UserProfile.objects.get(user=request.user)
                ticket.title = '[' + str(
                    entity.entity) + ']' + ' ' + ticket.title
                # Pour ajouter au titre l'entité à laquelle appartient
                # l'utilisateur pour une meilleur visibilité
            except:
                pass

            ticket.save()

            if USE_MAIL: # Dans le fichier de configuration settings.py
                send_new_ticket_all_staff.delay(ticket, request.user.email)
            return redirect(home)

        else:
            return render(request, 'add_ticket.html', locals())
    else:
        form = TicketForm(user=request.user)

    return render(request, 'add_ticket.html', locals())



@login_required(login_url='login/')
def ticket_list_new(request):
    """
    Retourne la page des tickets ouvert non assigné. Si le membre fait partie du staff
    tous les tickets sont affichés, sinon pour l'utilisateur seulement ses tickets seront affiché
    """
    if request.user.is_staff:
        list = Tickets.objects.filter(assign_to=None).order_by('-created')
        ticket_list = TicketsTables(list)
    else:
        list = Tickets.objects.filter(
            create_by=request.user,
            assign_to=None).order_by('-created')
        ticket_list = TicketsTables(list)

    RequestConfig(
        request,
        paginate={
            "per_page": 25}).configure(ticket_list)  # See django_tables2 Docs
    return render(request, 'ticket_list.html', {'ticket_list': ticket_list})



@login_required(login_url='login/')
def ticket_list_work(request):
    """
    Retourne la page des tickets ouvert. Si le membre fait partie du staff tous les tickets sont affichés,
    sinon pour l'utilisateur seulement ses tickets seront affiché
    """
    if request.user.is_staff:
        list = Tickets.objects.select_related('create_by', 'assign_to', 'category').prefetch_related('create_by',
                                                                                                     'category') \
            .filter(status='OPEN').exclude(assign_to=None).order_by('-created')
        ticket_list = TicketsTables(list)
    else:
        list = Tickets.objects.select_related('create_by', 'assign_to', 'category').prefetch_related('create_by',
                                                                                                     'category') \
            .filter(create_by=request.user, status='OPEN').exclude(assign_to=None).order_by('-created')
        ticket_list = TicketsTables(list)

    RequestConfig(
        request,
        paginate={
            "per_page": 25}).configure(ticket_list)  # See django_tables2 Docs
    return render(request, 'ticket_list.html', {'ticket_list': ticket_list})



@login_required(login_url='login/')
def ticket_list_resolved(request):
    """
    Retourne la page des tickets résolus. Si le membre fait partie du staff tous les tickets sont affichés,
    sinon pour l'utilisateur seulement ses tickets seront affiché
    """

    if request.user.is_staff:
        list = Tickets.objects.select_related('create_by', 'assign_to', 'category') \
            .filter(status='RESOLVED').exclude(assign_to=None).order_by('-created')
        ticket_list = TicketsTables(list)
    else:
        list = Tickets.objects.select_related('create_by', 'assign_to', 'category') \
            .prefetch_related('create_by', 'category') \
            .filter(create_by=request.user, status='RESOLVED').order_by('-created')
        ticket_list = TicketsTables(list)

    RequestConfig(
        request,
        paginate={
            "per_page": 25}).configure(ticket_list)  # See django_tables2 Docs
    return render(request, 'ticket_list.html', {'ticket_list': ticket_list})



@login_required(login_url='login/')
def ticket_list_clos(request):
    """
    Retourne la page des tickets clos. Si le membre fait partie du staff tous les tickets sont affichés,
    sinon pour l'utilisateur seulement ses tickets seront affiché
    """
    if request.user.is_staff:
        list = Tickets.objects.select_related('create_by', 'assign_to', 'category') \
            .prefetch_related('create_by', 'assign_to', 'category') \
            .filter(status='CLOSED').exclude(assign_to=None).order_by('-created')

        ticket_list = TicketsTables(list)
    else:
        list = Tickets.objects.select_related('create_by', 'assign_to', 'category') \
            .prefetch_related('create_by', 'category') \
            .filter(create_by=request.user, status='CLOSED').order_by('-created')

        ticket_list = TicketsTables(list)

    RequestConfig(
        request,
        paginate={
            "per_page": 25}).configure(ticket_list)  # See django_tables2 Docs
    return render(request, 'ticket_list.html', {'ticket_list': ticket_list})



@login_required(login_url='login/')
def ticket_all(request):
    """
    Retourne la page de tous les tickets pour le staff.
    """
    list = Tickets.objects.select_related(
        'create_by',
        'assign_to',
        'category').order_by('-created')
    ticket_list = TicketsTables(list)

    RequestConfig(
        request,
        paginate={
            "per_page": 25}).configure(ticket_list)  # See django_tables2 Docs
    return render(request, 'ticket_list.html', {'ticket_list': ticket_list})



@login_required(login_url='login/')
def ticket_edit(request, id):
    """
    :param id: ticket id
    Pour editer un ticket
    """
    ticket = get_object_or_404(Tickets, id=id)
    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user, instance=ticket)

        if form.is_valid():
            form.edit(ticket_id=id, user=request.user)
            #messages.add_message(request, messages.INFO, 'Ticket mis à jour OK')
            return redirect(view_ticket, id)
            # If the save was successful, redirect to another page
    else:
        form = TicketForm(user=request.user, instance=ticket)
        response = ResponseForm()

    return render(request, 'add_ticket.html', locals())




@login_required(login_url='login/')
def view_ticket(request, id):

    follow_up = Follow.objects.select_related(
                                            'follow_by',
                                            'ticket').filter(ticket=id)
    tickets = get_object_or_404(Tickets, id=id)

    if request.method == 'POST':
        form = ResponseForm(data=request.POST)
        ticket_form = StatusForm(request.POST, user=request.user, instance=tickets )
        print(ticket_form.errors)
        if form.is_valid() and ticket_form.is_valid() :
            print('coucou')
            if request.POST.get('status') == 'CLOSED':
                #try:
                ticket_form.close(ticket_id=id, user=request.user)

                #except Exception:
                    #messages.info(request, 'Vous devez clore le ticket %s' % tickets.depends_on)


            elif request.POST.get('status') == 'RESOLVED':
                tick = ticket_form.save(commit=False)
                ticket_form.edit(ticket_id=id, user=request.user)
                tick.status='RESOLVED'


            elif request.POST.get('status') == 'OPEN':
                tick = ticket_form.save(commit=False)
                ticket_form.edit(ticket_id=id, user=request.user)
                tick.status='OPEN'


        if request.POST.get('follow') == '':
            pass

        else:
            follow = form.save(commit=False)
            follow.ticket_id = id
            follow.follow_by = request.user
            follow.save()

    else:
        form = ResponseForm()
        ticket_form = StatusForm(instance=tickets, user=request.user)

    return render(request, 'ticket.html', locals())




@login_required(login_url='login/')
def my_ticket_assign(request):
    """
    Retourne la page de tous vos tickets assigné à vous.
    """
    list = Tickets.objects.filter(assign_to=request.user).select_related('create_by', 'assign_to', 'category'
                                                                         ).order_by('-created')
    ticket_list = TicketsTables(list)

    RequestConfig(
        request,
        paginate={
            "per_page": 25}).configure(ticket_list)  # See django_tables2 Docs
    return render(request, 'ticket_list.html', {'ticket_list': ticket_list})



@login_required(login_url='login/')
def delete_ticket(request, id):
    Follow.objects.filter(ticket_id=id).delete()
    Tickets.objects.filter(id=id).delete()
    return redirect('/')



@login_required(login_url='login/')
def set_incomplete(request, id):
    """
    Marque un ticket comme incomplet et attente d'informations complémentaire
    """
    ticket = Tickets.objects.get(pk=id)
    ticket.complete = 0
    ticket.save()

    return redirect('/ticket/id=%s' % (id))



@login_required(login_url='login/')
def set_complete(request, id):
    """
    Marque un ticket comme complet
    """
    ticket = Tickets.objects.get(pk=id)
    ticket.complete = 1
    ticket.save()
    return redirect('/ticket/id=%s' % (id))


@login_required(login_url='login/')
def ticket_list_incomplet(request):
    """
    Retourne la page des tickets clos. Si le membre fait partie du staff tous les tickets sont affichés,
    sinon pour l'utilisateur seulement ses tickets seront affiché
    """
    if request.user.is_staff:
        list = Tickets.objects.select_related('create_by', 'assign_to', 'category') \
                    .prefetch_related('create_by', 'assign_to', 'category') \
                    .filter(complete=0).order_by('-created')
        ticket_list = TicketsTables(list)
    else:
        list = Tickets.objects.select_related('create_by', 'assign_to', 'category') \
                    .prefetch_related('create_by', 'category') \
                    .filter(create_by=request.user, complete=0).order_by('-created')
        ticket_list = TicketsTables(list)

    RequestConfig(
        request,
        paginate={
            "per_page": 25}).configure(ticket_list)  # See django_tables2 Docs
    return render(request, 'ticket_list.html', {'ticket_list': ticket_list})








