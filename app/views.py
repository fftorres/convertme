# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import simplejson

from zencoder import Zencoder

from app.models import Video
from app.forms import VideoForm

"""
 upload:
   realiza upload dos arquivos para o servidor
   apos realizar o upload e salvar o registro, faz uma chamada a API do zencoder
   e retorna um json com o status e id do job 
"""
def upload(request):
    
    feedback = {} #sera usado para o retorno da acao
    
    if request.is_ajax() or request.method == 'POST':        
        form = VideoForm(request.POST, request.FILES)
        video = Video(file = request.FILES['file'])
        video.save()
        job = schedule_zencoder_job(video)
        
        if job.code == 201:
            feedback["status"] = "201" 
            feedback["job_id"] = job.body['id']
            video.job_id = job.body['id']
            video.save()
        else:
            feedback["status"] = "422"
            feedback["job_id"] = "0"
        
        return HttpResponse(simplejson.dumps(feedback), mimetype="application/json")
    else:
        form = VideoForm()

    feedback["status"] = "nok"
    feedback["job_id"] = "0"
    
    return HttpResponse(simplejson.dumps(feedback), mimetype="application/json")
    
"""
  Funcao auxiliar para criar o job no Zencoder
  Mover depois para dentro de um local mais apropriado
"""    
def schedule_zencoder_job(video_obj):
    zen = Zencoder("7f188a0403a4caac59d8a0080015cae9", api_version = "v2", as_xml = False, test = True)

    nome_arquivo = video_obj.file.name.split("/")[-1] + ".wmv" #pega apenas o nome do arquivo e coloca a extensao wmv
    output = {}
    output["url"] = "s3://nandotorres/%s" % nome_arquivo 
    output["base_url"] = "s3://nandotorres/"
    output["format"]   = "wmv"
    output["notifications"] = [{ "url": ("%s/notify/%s" % (settings.SITE_URL, video_obj.id)) }]
    
    job = zen.job.create(settings.SITE_URL + settings.MEDIA_URL + video_obj.file.name, output)
    
    return job
    
"""
 Acao para que o zencoder possa notificar que um job foi concluido
"""
def notify(request, video_id = 0):
    video = Video.objects.get(id = video_id)
    video.job_done = True
    video.save()
    return HttpResponse(simplejson.dumps({'status': 'ok'}), mimetype="application/json")