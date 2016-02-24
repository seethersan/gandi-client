import xmlrpclib
import time
from gandi.forms import BuscarDominioForm
from gandi.models import Dominio, countries
from gandi.forms import UserForm, precioProducto, precioDominio, registroAtencion
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from cartridge.shop.models import Product, ProductVariation, Priced
from django.db.models import Count
from cartridge.shop.utils import recalculate_cart
from datetime import datetime, date, timedelta
from calendarium.models import Event
from django.views.decorators.cache import cache_page
from django.conf import settings

api = xmlrpclib.ServerProxy('https://rpc.gandi.net/xmlrpc/')
apikey = settings.APIKEY

@cache_page(60)
def buscarDominio(request):
	resultado = ''
	domain = ''
	dominio = ''
	extension = ''
	precio = ''
	duracion = 1
	descripcion = ''
	precio_total = ''
	price_unit = ''
        if request.method=='POST' and 'buscar' in request.POST:
                consulta = BuscarDominioForm(request.POST)
                if consulta.is_valid():
                        dominio = consulta.cleaned_data['dominio']
			extension = consulta.cleaned_data['extension']
			duracion = consulta.cleaned_data['duracion']
			duracion = int(duracion)
			request.session['dur'] = duracion
			dominio = str(dominio)
			sufijo = str(extension)
			domain = dominio + '.' + sufijo
			request.session['dom'] = domain
			result = api.domain.available(apikey, [domain])
	                while result[domain]  == 'pending':
        	        	time.sleep(0.7)
                		result = api.domain.available(apikey, [domain])
				if result[domain] == 'available':
					resultado = domain + ' se encuentra disponible'
					product_spec = {
						'product' : {
							'description': domain,
							'type': 'domain'
						},
						'action' : {
							'name': 'create',
							'duration': duracion
						}
					}
					result = api.catalog.list(apikey, product_spec)
					result2 = result[0]
					price = result2['unit_price']
					price2 = price[0]
					price_unit = price2['price']
					precio = (price_unit + 4)*4
					request.session['pr_un'] = price_unit
					request.session['pre'] = precio
					precio_total = precio*duracion
					break
				elif result[domain] == 'unavailable':
					resultado = domain + ' no se encuentra disponible'
					break
				request.session['res'] = resultado
        elif request.method == 'POST' and 'registro' in request.POST:
		producto = Product()
                dominio = request.session.get('dom')
		dominio = str(dominio)
                unit_price = request.session.get('pr_un')
               	sale_price = request.session.get('pre')
		producto.unit_price = unit_price
		producto.sale_price = sale_price
		producto.num_in_stock = 30
		producto.sku = Product.objects.all().count() + 1
                duracion = request.session.get('dur')
		producto.available = True
		producto.title = dominio
		producto.save()
                product = ProductVariation()
                product.product = producto
		product.unit_price = unit_price
		product.sale_price = sale_price
		product.num_in_stock = 30
		product.sku = ProductVariation.objects.all().count() + 1
		product.save()
                request.cart.add_item(product, duracion)
		recalculate_cart(request)
		return HttpResponseRedirect('/shop/cart/')
        else:
                consulta = BuscarDominioForm()
        return render_to_response('buscadominioform.html',{'consulta':consulta, 'resultado':resultado, 'precio':precio_total}, context_instance=RequestContext(request))


def nuevoUsuario(request):
	mensaje = ''
        if request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/')
	else:
		if request.method == 'POST':
			form = UserForm(request.POST)
			if form.is_valid():
				user = form.cleaned_data['usuario']
				email = form.cleaned_data['correo']
				first_name = form.cleaned_data['nombres']
				last_name = form.cleaned_data['apellidos']
				direccion = form.cleaned_data['direccion']
				password1 = form.cleaned_data['password1']
				password2 = form.cleaned_data['password2']
				if password1 == password2:
					password = password1
				else:
					form = UserForm()
				zip = form.cleaned_data['zip']
				city = form.cleaned_data['ciudad']
				tipo = form.cleaned_data['tipo']
				pais = form.cleaned_data['pais']
				phone = form.cleaned_data['telefono']
				new_user = User.objects.create_user(username=user,password=password,pais_id=pais)
				new_user.first_name=first_name
				new_user.email=email
				new_user.last_name=last_name
				new_user.direccion=direccion
				new_user.zip=zip
				new_user.ciudad=city
				new_user.telefono=phone
				new_user.save()
				return HttpResponseRedirect('/accounts/login/')
		else:	
			form = UserForm()
	return render_to_response('registro.html',{'form':form}, context_instance=RequestContext(request))

def nuevaAtencion(request):
	formato = "%m-%d-%y %H:%M"
	if request.user.is_authenticated():
		if request.method == 'POST':
			form = registroAtencion(request.POST)
			if form.is_valid():
				start = form.cleaned_data['fecha']
				if start.date() >= date.today():
					duracion = int(form.cleaned_data['duracion'])
					end = start + timedelta(hours = duracion)
					descripcion = form.cleaned_data['descripcion']
					titulo = form.cleaned_data['titulo']
					atencion = Event()
					atencion.start = start
					atencion.end = end
					atencion.description = descripcion
					atencion.created_by = request.user
					atencion.title = titulo
					atencion.save()
					return HttpResponseRedirect('/calendar/')
				else:
					form = registroAtencion(request.POST)
		else:
			form = registroAtencion()
	else:
		return HttpResponseRedirect('/accounts/login/')
	return render_to_response('atencion.html',{'form':form}, context_instance=RequestContext(request))

