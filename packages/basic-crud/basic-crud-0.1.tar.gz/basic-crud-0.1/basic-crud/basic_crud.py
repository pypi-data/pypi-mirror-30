# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404


# Create a basic object
def new_object(request, form, operation, template_name, redirect_success):
    context = dict()

    object_form = form(request.POST or None, prefix='object')

    if request.method == 'POST':
        if object_form.is_valid():
            object_form.save()
            return redirect(redirect_success)
        else:
            context['errors'] = object_form.errors

    context['edit'] = False
    context['form'] = object_form
    context['operation'] = operation

    return render(request=request, template_name=template_name, context=context)


# Update a basic object
def update_object(request, pk, object_model, form, operation, template_name, redirect_success):
    context = dict()

    object_instance = get_object_or_404(object_model, pk=pk)
    object_form = form(request.POST or None, instance=object_instance)

    if request.method == 'POST':
        if object_form.is_valid():
            object_form.save()

            return redirect(redirect_success)
        else:
            context['errors'] = object_form.errors
    else:
        object_form = form(instance=object_instance)

    context['form'] = object_form
    context['operation'] = operation
    context['edit'] = True
    return render(request=request, template_name=template_name, context=context)


# Delete ajax object
def delete_object(request, pk, object_model):
    if request.method == 'POST':
        try:
            object_instance = object_model.objects.get(pk=pk)
        except object_model.DoesNotExist:
            return JsonResponse('Does Not Exist', status=404, safe=False)
        object_instance.delete()
        return JsonResponse('Success', status=200, safe=False)
    else:
        return JsonResponse('Bad Request', status=405, safe=False)
