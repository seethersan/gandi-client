from django.db import models
from django.contrib.auth.models import User
from mezzanine.pages.models import Page
# Create your models here.

class countries(models.Model):
        id = models.SmallIntegerField()
        country_code = models.CharField(max_length=2,primary_key=True)
        country_name = models.CharField(max_length=100)

User.add_to_class('direccion', models.CharField(null=False,blank=False,max_length=30))
User.add_to_class('zip', models.CharField(null=True,blank=True,max_length=12))
User.add_to_class('ciudad', models.CharField(null=False,blank=False,max_length=30))
User.add_to_class('pais', models.ForeignKey(countries))
User.add_to_class('telefono', models.CharField(null=False,blank=False,max_length=12))
User.add_to_class('tipo', models.CharField(max_length=1,null=False,blank=False))

class Contacto(models.Model):
	user = models.ForeignKey(User, unique=True)
	gandiuser = models.CharField(max_length=12,null=False,blank=False, primary_key=True)

class Dominio(models.Model):
	dominio = models.TextField(help_text='Ingrese su Dominio', primary_key=True)
	owner = models.ForeignKey(Contacto)
	admin = models.CharField(max_length=12)
	bill = models.CharField(max_length=12)
	tech = models.CharField(max_length=12)
	nameserver1 = models.TextField(help_text='Ingrese DNS principal')
	nameserver2 = models.TextField(help_text='Ingrese DNS secundarios')
	nameserver3 = models.TextField(help_text='Ingrese DNS secundarios')
	nameserver4 = models.TextField(help_text='Ingrese DNS secundarios')
	def __unicode__(self):
		return self.dominio

	




